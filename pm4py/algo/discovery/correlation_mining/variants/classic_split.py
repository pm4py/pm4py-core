'''
PM4Py – A Process Mining Library for Python
Copyright (C) 2026 Process Intelligence Solutions GmbH

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see this software project's root or
visit <https://www.gnu.org/licenses/>.

Website: https://processintelligence.solutions
Contact: info@processintelligence.solutions
'''
from pm4py.util import exec_utils
from enum import Enum
from pm4py.util import constants, xes_constants, pandas_utils
from pm4py.objects.conversion.log import converter
from pm4py.algo.discovery.correlation_mining.variants import classic
from collections import Counter
import numpy as np
from typing import Optional, Dict, Any, Union, Tuple
from pm4py.objects.log.obj import EventLog, EventStream
from pm4py.utils import is_polars_lazyframe
import pandas as pd
import importlib.util


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    SAMPLE_SIZE = "sample_size"


def apply(
    log: Union[EventLog, EventStream, pd.DataFrame],
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> Tuple[Dict[Tuple[str, str], int], Dict[Tuple[str, str], float]]:
    """
    Applies the correlation miner (splits the log in smaller chunks)

    Parameters
    ---------------
    log
        Log object
    parameters
        Parameters of the algorithm

    Returns
    ---------------
    dfg
        Frequency DFG
    performance_dfg
        Performance DFG
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(
        Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY
    )
    timestamp_key = exec_utils.get_param_value(
        Parameters.TIMESTAMP_KEY,
        parameters,
        xes_constants.DEFAULT_TIMESTAMP_KEY,
    )
    start_timestamp_key = exec_utils.get_param_value(
        Parameters.START_TIMESTAMP_KEY,
        parameters,
        xes_constants.DEFAULT_TIMESTAMP_KEY,
    )
    sample_size = exec_utils.get_param_value(
        Parameters.SAMPLE_SIZE, parameters, 100000
    )

    PS_matrixes = []
    duration_matrixes = []

    if pandas_utils.check_is_pandas_dataframe(log):
        if is_polars_lazyframe(log):
            if importlib.util.find_spec("polars") is None:
                raise RuntimeError(
                    "Polars LazyFrame provided but 'polars' package is not installed."
                )

            import polars as pl  # type: ignore[import-untyped]

            required_columns = list(
                {activity_key, timestamp_key, start_timestamp_key}
            )
            missing_columns = [
                col for col in required_columns if col not in log.columns
            ]
            if missing_columns:
                raise Exception(
                    "The provided Polars LazyFrame does not contain the following required columns: "
                    + ", ".join(sorted(missing_columns))
                )

            activities_counter = (
                log.group_by(activity_key)
                .agg(pl.len().alias("__pm4py_count__"))
                .collect()
            )
            activities_counter = {
                row[activity_key]: row["__pm4py_count__"]
                for row in activities_counter.iter_rows(named=True)
            }
            activities = sorted(list(activities_counter.keys()))

            log = (
                log.select(required_columns)
                .sort([timestamp_key, start_timestamp_key], maintain_order=True)
                .collect()
                .to_pandas()
            )
        else:
            # code for Pandas dataframes
            log = log[
                list(set([activity_key, timestamp_key, start_timestamp_key]))
            ]
            log = log.sort_values([timestamp_key, start_timestamp_key])
            activities_counter = log[activity_key].value_counts().to_dict()
            activities = sorted(list(activities_counter.keys()))
    else:
        log = converter.apply(
            log,
            variant=converter.Variants.TO_EVENT_STREAM,
            parameters={"deepcopy": False, "include_case_attributes": False},
        )
        activities_counter = Counter(x[activity_key] for x in log)
        activities = sorted(list(activities_counter.keys()))

    prev = 0
    while prev < len(log):
        sample = log[prev: min(len(log), prev + sample_size)]
        transf_stream, activities_grouped, activities = classic.preprocess_log(
            sample, activities=activities, parameters=parameters
        )
        PS_matrix, duration_matrix = classic.get_PS_dur_matrix(
            activities_grouped, activities, parameters=parameters
        )
        PS_matrixes.append(PS_matrix)
        duration_matrixes.append(duration_matrix)

        prev = prev + sample_size

    PS_matrix = np.zeros((len(activities), len(activities)))
    duration_matrix = np.zeros((len(activities), len(activities)))
    z = 0
    while z < len(PS_matrixes):
        PS_matrix = PS_matrix + PS_matrixes[z]
        duration_matrix = np.maximum(duration_matrix, duration_matrixes[z])
        z = z + 1
    PS_matrix = PS_matrix / float(len(PS_matrixes))

    return classic.resolve_lp_get_dfg(
        PS_matrix, duration_matrix, activities, activities_counter
    )

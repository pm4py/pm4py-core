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
from enum import Enum
from typing import Optional, Dict, Any, Union

import importlib.util

from pm4py.util import xes_constants, constants, exec_utils, pandas_utils
from pm4py.algo.discovery.causal import algorithm as causal_discovery


class Outputs(Enum):
    DFG = "dfg"
    SEQUENCE = "sequence"
    PARALLEL = "parallel"
    START_ACTIVITIES = "start_activities"
    END_ACTIVITIES = "end_activities"
    ACTIVITIES = "activities"
    SKIPPABLE = "skippable"
    ACTIVITIES_ALWAYS_HAPPENING = "activities_always_happening"
    MIN_TRACE_LENGTH = "min_trace_length"
    TRACE = "trace"


class Parameters(Enum):
    SORT_REQUIRED = "sort_required"
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    INDEX_KEY = "index_key"


DEFAULT_SORT_REQUIRED = True
DEFAULT_INDEX_KEY = "@@index"


def apply(
    lf,
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> Dict[str, Any]:
    if parameters is None:
        parameters = {}

    if importlib.util.find_spec("polars") is None:
        raise RuntimeError(
            "Polars LazyFrame provided but 'polars' package is not installed."
        )

    import polars as pl  # type: ignore[import-untyped]
    from pm4py.algo.discovery.dfg.adapters.polars import df_statistics

    activity_key = exec_utils.get_param_value(
        Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY
    )
    caseid_key = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME
    )
    start_timestamp_key = exec_utils.get_param_value(
        Parameters.START_TIMESTAMP_KEY, parameters, None
    )
    timestamp_key = exec_utils.get_param_value(
        Parameters.TIMESTAMP_KEY,
        parameters,
        xes_constants.DEFAULT_TIMESTAMP_KEY,
    )
    sort_required = exec_utils.get_param_value(
        Parameters.SORT_REQUIRED, parameters, DEFAULT_SORT_REQUIRED
    )
    index_key = exec_utils.get_param_value(
        Parameters.INDEX_KEY, parameters, DEFAULT_INDEX_KEY
    )

    required_columns = {caseid_key, activity_key, timestamp_key}
    if start_timestamp_key is not None:
        required_columns.add(start_timestamp_key)

    if hasattr(lf, "collect_schema"):
        lf_columns = lf.collect_schema().names()
    else:
        lf_columns = lf.columns

    missing_columns = [col for col in required_columns if col not in lf_columns]
    if missing_columns:
        raise Exception(
            "The provided Polars LazyFrame does not contain the following required columns: "
            + ", ".join(sorted(missing_columns))
        )

    lf_selected = lf.select(list(required_columns))

    if sort_required:
        lf_selected = pandas_utils.insert_index(
            lf_selected, column_name=index_key, copy_dataframe=False
        )

        sort_columns = [caseid_key]
        if start_timestamp_key is not None:
            sort_columns.append(start_timestamp_key)
        sort_columns.append(timestamp_key)
        sort_columns.append(index_key)

        lf_selected = lf_selected.sort(sort_columns, maintain_order=True)

    dfg = df_statistics.get_dfg_graph(
        lf_selected,
        measure="frequency",
        activity_key=activity_key,
        case_id_glue=caseid_key,
        timestamp_key=timestamp_key,
        sort_caseid_required=False,
        sort_timestamp_along_case_id=False,
        start_timestamp_key=start_timestamp_key,
    )

    activities_df = (
        lf_selected.select(pl.col(activity_key).unique().alias("__act__"))
        .collect()
    )
    activities = set(activities_df["__act__"].to_list())

    grouped = lf_selected.group_by(caseid_key)
    first_df = grouped.agg(pl.col(activity_key).first().alias("__first__"))
    last_df = grouped.agg(pl.col(activity_key).last().alias("__last__"))

    start_activities = set(first_df.collect()["__first__"].to_list())
    end_activities = set(last_df.collect()["__last__"].to_list())

    parallel = {(x, y) for (x, y) in dfg if (y, x) in dfg}
    sequence = set(
        causal_discovery.apply(dfg, causal_discovery.Variants.CAUSAL_ALPHA)
    )

    min_trace_length_df = grouped.agg(pl.len().alias("__size__")).collect()
    min_trace_length = int(min_trace_length_df["__size__"].min())

    ret: Dict[str, Any] = {}
    ret[Outputs.DFG.value] = dfg
    ret[Outputs.SEQUENCE.value] = sequence
    ret[Outputs.PARALLEL.value] = parallel
    ret[Outputs.ACTIVITIES.value] = activities
    ret[Outputs.START_ACTIVITIES.value] = start_activities
    ret[Outputs.END_ACTIVITIES.value] = end_activities
    ret[Outputs.MIN_TRACE_LENGTH.value] = min_trace_length

    return ret


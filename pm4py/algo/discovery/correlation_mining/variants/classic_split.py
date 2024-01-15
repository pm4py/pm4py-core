'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
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
import pandas as pd


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    SAMPLE_SIZE = "sample_size"


def apply(log: Union[EventLog, EventStream, pd.DataFrame], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Tuple[Dict[Tuple[str, str], int], Dict[Tuple[str, str], float]]:
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

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters,
                                                     xes_constants.DEFAULT_TIMESTAMP_KEY)
    sample_size = exec_utils.get_param_value(Parameters.SAMPLE_SIZE, parameters, 100000)

    PS_matrixes = []
    duration_matrixes = []

    if pandas_utils.check_is_pandas_dataframe(log):
        # keep only the two columns before conversion
        log = log[list(set([activity_key, timestamp_key, start_timestamp_key]))]
        log = log.sort_values([timestamp_key, start_timestamp_key])
        activities_counter = log[activity_key].value_counts().to_dict()
        activities = sorted(list(activities_counter.keys()))
    else:
        log = converter.apply(log, variant=converter.Variants.TO_EVENT_STREAM, parameters={"deepcopy": False, "include_case_attributes": False})
        activities_counter = Counter(x[activity_key] for x in log)
        activities = sorted(list(activities_counter.keys()))

    prev = 0
    while prev < len(log):
        sample = log[prev:min(len(log), prev + sample_size)]
        transf_stream, activities_grouped, activities = classic.preprocess_log(sample, activities=activities,
                                                                               parameters=parameters)
        PS_matrix, duration_matrix = classic.get_PS_dur_matrix(activities_grouped, activities,
                                                               parameters=parameters)
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

    return classic.resolve_lp_get_dfg(PS_matrix, duration_matrix, activities, activities_counter)

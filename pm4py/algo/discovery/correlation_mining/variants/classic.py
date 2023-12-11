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
from pm4py.objects.log.obj import Event
from pm4py.algo.discovery.correlation_mining import util as cm_util
import numpy as np
from typing import Optional, Dict, Any, Union, Tuple
from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    EXACT_TIME_MATCHING = "exact_time_matching"
    INDEX_KEY = "index_key"


DEFAULT_INDEX_KEY = "@@@index"


def apply(log: Union[EventLog, EventStream, pd.DataFrame], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Tuple[Dict[Tuple[str, str], int], Dict[Tuple[str, str], float]]:
    """
    Apply the correlation miner to an event stream
    (other types of logs are converted to that)

    The approach is described in:
    Pourmirza, Shaya, Remco Dijkman, and Paul Grefen. "Correlation miner: mining business process models and event
    correlations without case identifiers." International Journal of Cooperative Information Systems 26.02 (2017):
    1742002.

    Parameters
    ---------------
    log
        Log object
    parameters
        Parameters of the algorithm

    Returns
    ---------------
    dfg
        DFG
    performance_dfg
        Performance DFG (containing the estimated performance for the arcs)
    """
    if parameters is None:
        parameters = {}

    transf_stream, activities_grouped, activities = preprocess_log(log, parameters=parameters)

    PS_matrix, duration_matrix = get_PS_dur_matrix(activities_grouped, activities, parameters=parameters)
    activities_counter = {x: len(y) for x, y in activities_grouped.items()}

    return resolve_lp_get_dfg(PS_matrix, duration_matrix, activities, activities_counter)


def resolve_lp_get_dfg(PS_matrix, duration_matrix, activities, activities_counter):
    """
    Resolves a LP problem to get a DFG

    Parameters
    --------------
    PS_matrix
        Precede-succeed matrix
    duration_matrix
        Duration matrix
    activities
        List of activities of the log
    activities_counter
        Counter of the activities

    Returns
    --------------
    dfg
        DFG
    performance_dfg
        Performance DFG (containing the estimated performance for the arcs)
    """
    C_matrix = cm_util.get_c_matrix(PS_matrix, duration_matrix, activities, activities_counter)
    dfg, performance_dfg = cm_util.resolve_LP(C_matrix, duration_matrix, activities, activities_counter)
    return dfg, performance_dfg


def get_PS_dur_matrix(activities_grouped, activities, parameters=None):
    """
    Combined methods to get the two matrixes

    Parameters
    ----------------
    activities_grouped
        Grouped activities
    activities
        List of activities of the log
    parameters
        Parameters of the algorithm

    Returns
    ---------------
    PS_matrix
        Precede-succeed matrix
    duration_matrix
        Duration matrix
    """
    if parameters is None:
        parameters = {}

    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters,
                                                     xes_constants.DEFAULT_TIMESTAMP_KEY)
    exact_time_matching = exec_utils.get_param_value(Parameters.EXACT_TIME_MATCHING, parameters, False)

    PS_matrix = get_precede_succeed_matrix(activities, activities_grouped, timestamp_key, start_timestamp_key)
    duration_matrix = get_duration_matrix(activities, activities_grouped, timestamp_key, start_timestamp_key,
                                          exact=exact_time_matching)

    return PS_matrix, duration_matrix


def preprocess_log(log, activities=None, parameters=None):
    """
    Preprocess a log to enable correlation mining

    Parameters
    --------------
    log
        Log object
    activities
        (if provided) list of activities of the log
    parameters
        Parameters of the algorithm

    Returns
    --------------
    transf_stream
        Transformed stream
    activities_grouped
        Grouped activities
    activities
        List of activities of the log
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters,
                                                     xes_constants.DEFAULT_TIMESTAMP_KEY)
    index_key = exec_utils.get_param_value(Parameters.INDEX_KEY, parameters, DEFAULT_INDEX_KEY)

    if pandas_utils.check_is_pandas_dataframe(log):
        # keep only the two columns before conversion
        log = log[list(set([activity_key, timestamp_key, start_timestamp_key]))]

    parameters["deepcopy"] = False
    parameters["include_case_attributes"] = False
    log = converter.apply(log, variant=converter.TO_EVENT_STREAM, parameters=parameters)
    transf_stream = EventStream()
    for idx, ev in enumerate(log):
        transf_stream.append(
            Event({activity_key: ev[activity_key], timestamp_key: ev[timestamp_key].timestamp(),
                   start_timestamp_key: ev[start_timestamp_key].timestamp(), index_key: idx}))
    transf_stream = sorted(transf_stream, key=lambda x: (x[start_timestamp_key], x[timestamp_key], x[index_key]))

    if activities is None:
        activities = sorted(list(set(x[activity_key] for x in transf_stream)))

    activities_grouped = {x: [y for y in transf_stream if y[activity_key] == x] for x in activities}

    return transf_stream, activities_grouped, activities


def get_precede_succeed_matrix(activities, activities_grouped, timestamp_key, start_timestamp_key):
    """
    Calculates the precede succeed matrix

    Parameters
    ---------------
    activities
        Ordered list of activities of the log
    activities_grouped
        Grouped list of activities
    timestamp_key
        Timestamp key
    start_timestamp_key
        Start timestamp key (events start)

    Returns
    ---------------
    precede_succeed_matrix
        Precede succeed matrix
    """
    ret = np.zeros((len(activities), len(activities)))
    for i in range(len(activities)):
        ai = [x[timestamp_key] for x in activities_grouped[activities[i]]]
        if ai:
            for j in range(len(activities)):
                if not i == j:
                    aj = [x[start_timestamp_key] for x in activities_grouped[activities[j]]]
                    if aj:
                        k = 0
                        z = 0
                        count = 0
                        while k < len(ai):
                            while z < len(aj):
                                if ai[k] < aj[z]:
                                    break
                                z = z + 1
                            count = count + (len(aj) - z)
                            k = k + 1
                        ret[i, j] = count / float(len(ai) * len(aj))

    return ret


def get_duration_matrix(activities, activities_grouped, timestamp_key, start_timestamp_key, exact=False):
    """
    Calculates the duration matrix

    Parameters
    ---------------
    activities
        Ordered list of activities of the log
    activities_grouped
        Grouped list of activities
    timestamp_key
        Timestamp key
    start_timestamp_key
        Start timestamp key (events start)
    exact
        Performs an exact matching of the times (True/False)

    Returns
    ---------------
    duration_matrix
        Duration matrix
    """
    # greedy algorithm
    ret = np.zeros((len(activities), len(activities)))
    for i in range(len(activities)):
        ai = [x[timestamp_key] for x in activities_grouped[activities[i]]]
        if ai:
            for j in range(len(activities)):
                if not i == j:
                    aj = [x[start_timestamp_key] for x in activities_grouped[activities[j]]]
                    if aj:
                        ret[i, j] = cm_util.match_return_avg_time(ai, aj, exact=exact)
    return ret

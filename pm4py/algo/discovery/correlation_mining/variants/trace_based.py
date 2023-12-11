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
from pm4py.algo.discovery.correlation_mining import util as cm_util
from statistics import mean
import numpy as np
from collections import Counter
from typing import Optional, Dict, Any, Union, Tuple
from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    INDEX_KEY = "index_key"


DEFAULT_INDEX_KEY = "@@@index"


def apply(log: Union[EventLog, EventStream, pd.DataFrame], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Tuple[Dict[Tuple[str, str], int], Dict[Tuple[str, str], float]]:
    """
    Novel approach of correlation mining, that creates the PS-matrix and the duration matrix
    using the order list of events of each trace of the log

    Parameters
    -------------
    log
        Event log
    parameters
        Parameters

    Returns
    ---------------
    dfg
        DFG
    performance_dfg
        Performance DFG (containing the estimated performance for the arcs)
    """
    traces_list, trace_grouped_list, activities, activities_counter = preprocess_log(log, activities=None,
                                                                                     activities_counter=None)

    PS_matrix, duration_matrix = get_PS_duration_matrix(activities, trace_grouped_list, parameters=parameters)

    return resolve_lp_get_dfg(PS_matrix, duration_matrix, activities, activities_counter)


def resolve_lp_get_dfg(PS_matrix, duration_matrix, activities, activities_counter):
    """
    Resolves a LP problem to get a DFG

    Parameters
    ---------------
    PS_matrix
        Precede-succeed matrix
    duration_matrix
        Duration matrix
    activities
        List of activities of the log
    activities_counter
        Counter for the activities of the log

    Returns
    ---------------
    dfg
        Frequency DFG
    performance_dfg
        Performance DFG
    """
    C_matrix = cm_util.get_c_matrix(PS_matrix, duration_matrix, activities, activities_counter)
    dfg, performance_dfg = cm_util.resolve_LP(C_matrix, duration_matrix, activities, activities_counter)
    return dfg, performance_dfg


def get_PS_duration_matrix(activities, trace_grouped_list, parameters=None):
    """
    Gets the precede-succeed matrix

    Parameters
    --------------
    activities
        Activities
    trace_grouped_list
        Grouped list of simplified traces (per activity)
    parameters
        Parameters of the algorithm

    Returns
    --------------
    PS_matrix
        precede-succeed matrix
    duration_matrix
        Duration matrix
    """
    if parameters is None:
        parameters = {}

    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters,
                                                     xes_constants.DEFAULT_TIMESTAMP_KEY)

    PS_matrix = get_precede_succeed_matrix(activities, trace_grouped_list, timestamp_key, start_timestamp_key)
    duration_matrix = get_duration_matrix(activities, trace_grouped_list, timestamp_key, start_timestamp_key)

    return PS_matrix, duration_matrix


def preprocess_log(log, activities=None, activities_counter=None, parameters=None):
    """
    Preprocess the log to get a grouped list of simplified traces (per activity)

    Parameters
    --------------
    log
        Log object
    activities
        (if provided) activities of the log
    activities_counter
        (if provided) counter of the activities of the log
    parameters
        Parameters of the algorithm

    Returns
    --------------
    traces_list
        List of simplified traces of the log
    trace_grouped_list
        Grouped list of simplified traces (per activity)
    activities
        Activities of the log
    activities_counter
        Activities counter
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters,
                                                     xes_constants.DEFAULT_TIMESTAMP_KEY)
    caseid_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
    index_key = exec_utils.get_param_value(Parameters.INDEX_KEY, parameters, DEFAULT_INDEX_KEY)

    if pandas_utils.check_is_pandas_dataframe(log):
        # keep only the two columns before conversion
        log = log[list(set([activity_key, timestamp_key, start_timestamp_key, caseid_key]))]

    log = converter.apply(log, variant=converter.Variants.TO_EVENT_LOG, parameters=parameters)

    traces_list = []
    for trace in log:
        trace_stream = [
            {activity_key: trace[i][activity_key], timestamp_key: trace[i][timestamp_key].timestamp(),
             start_timestamp_key: trace[i][start_timestamp_key].timestamp(), index_key: i} for
            i in range(len(trace))]
        trace_stream = sorted(trace_stream, key=lambda x: (x[start_timestamp_key], x[timestamp_key], x[index_key]))
        traces_list.append(trace_stream)

    if activities is None:
        activities = sorted(list(set(y[activity_key] for x in traces_list for y in x)))

    trace_grouped_list = []
    for trace in traces_list:
        gr = []
        for act in activities:
            act_gr = [x for x in trace if x[activity_key] == act]
            gr.append(act_gr)
        trace_grouped_list.append(gr)

    if activities_counter is None:
        activities_counter = Counter(y[activity_key] for x in traces_list for y in x)

    return traces_list, trace_grouped_list, activities, activities_counter


def get_precede_succeed_matrix(activities, trace_grouped_list, timestamp_key, start_timestamp_key):
    """
    Calculates the precede succeed matrix

    Parameters
    ---------------
    activities
        Sorted list of activities of the log
    trace_grouped_list
        A list of lists of lists, containing for each trace and each activity the events having such activity
    timestamp_key
        The key to be used as timestamp
    start_timestamp_key
        The key to be used as start timestamp

    Returns
    ---------------
    mat
        The precede succeed matrix
    """
    ret = np.zeros((len(activities), len(activities)))
    for i in range(len(activities)):
        for j in range(len(activities)):
            if not i == j:
                count = 0
                total = 0
                for tr in trace_grouped_list:
                    ai = [x[timestamp_key] for x in tr[i]]
                    aj = [x[start_timestamp_key] for x in tr[j]]
                    if ai and aj:
                        total += len(ai) * len(aj)
                        k = 0
                        z = 0
                        while k < len(ai):
                            while z < len(aj):
                                if ai[k] < aj[z]:
                                    break
                                z = z + 1
                            count = count + (len(aj) - z)
                            k = k + 1
                if total > 0:
                    ret[i, j] = count / float(total)
    return ret


def get_duration_matrix(activities, trace_grouped_list, timestamp_key, start_timestamp_key):
    """
    Calculates the duration matrix

    Parameters
    --------------
    activities
        Sorted list of activities of the log
    trace_grouped_list
        A list of lists of lists, containing for each trace and each activity the events having such activity
    timestamp_key
        The key to be used as timestamp
    start_timestamp_key
        The key to be used as start timestamp

    Returns
    --------------
    mat
        The duration matrix
    """
    ret = np.zeros((len(activities), len(activities)))
    for i in range(len(activities)):
        for j in range(len(activities)):
            if not i == j:
                tm0 = []
                tm1 = []
                for tr in trace_grouped_list:
                    ai = [x[timestamp_key] for x in tr[i]]
                    aj = [x[start_timestamp_key] for x in tr[j]]
                    if ai and aj:
                        tm0 = cm_util.calculate_time_match_fifo(ai, aj, times0=tm0)
                        tm1 = cm_util.calculate_time_match_rlifo(ai, aj, times1=tm1)
                td0 = mean([x[1] - x[0] for x in tm0]) if tm0 else 0
                td1 = mean([x[1] - x[0] for x in tm1]) if tm1 else 0
                ret[i, j] = min(td0, td1)
    return ret

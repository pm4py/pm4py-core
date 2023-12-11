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
from copy import copy
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, Tuple

from numpy.random import choice, exponential

from pm4py.objects.log.obj import EventLog, Trace, Event
from pm4py.util import exec_utils, constants, xes_constants
from pm4py.util.dt_parsing.variants import strpfromiso


class Parameters(Enum):
    NUM_TRACES = "num_traces"
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    CASE_ARRIVAL_RATE = "case_arrival_rate"
    PERFORMANCE_DFG = "performance_dfg"
    PARAM_ARTIFICIAL_START_ACTIVITY = constants.PARAM_ARTIFICIAL_START_ACTIVITY
    PARAM_ARTIFICIAL_END_ACTIVITY = constants.PARAM_ARTIFICIAL_END_ACTIVITY


def dict_based_choice(dct: Dict[str, float]) -> str:
    """
    Performs a weighted choice, given a dictionary associating
    a weight to each possible choice

    Parameters
    -----------------
    dct
        Dictionary associating a weight to each choice

    Returns
    -----------------
    choice
        Choice
    """
    X = []
    Y = []
    summ = 0
    for x, y in dct.items():
        X.append(x)
        Y.append(y)
        summ += y
    if summ > 0:
        for i in range(len(Y)):
            Y[i] = Y[i] / summ
        return list(choice(X, 1, p=Y))[0]


def apply(frequency_dfg: Dict[Tuple[str, str], int], start_activities: Dict[str, int], end_activities: Dict[str, int],
          parameters: Optional[Dict[Any, Any]] = None) -> EventLog:
    """
    Simulates a log out with the transition probabilities provided by the frequency DFG,
    and the time deltas provided by the performance DFG

    Parameters
    ---------------
    frequency_dfg
        Frequency DFG
    start_activities
        Start activities
    end_activities
        End activities
    parameters
        Parameters of the algorithm, including:
        - Parameters.NUM_TRACES: the number of traces of the simulated log
        - Parameters.ACTIVITY_KEY: the activity key to be used in the simulated log
        - Parameters.TIMESTAMP_KEY: the timestamp key to be used in the simulated log
        - Parameters.CASE_ID_KEY: the case identifier key to be used in the simulated log
        - Parameters.CASE_ARRIVAL_RATE: the average distance (in seconds) between the start of two cases (default: 1)
        - Parameters.PERFORMANCE_DFG: (mandatory) the performance DFG that is used for the time deltas.

    Returns
    ---------------
    simulated_log
        Simulated log
    """
    if parameters is None:
        parameters = {}

    num_traces = exec_utils.get_param_value(Parameters.NUM_TRACES, parameters, 1000)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, xes_constants.DEFAULT_TRACEID_KEY)
    case_arrival_rate = exec_utils.get_param_value(Parameters.CASE_ARRIVAL_RATE, parameters, 1)
    performance_dfg = copy(exec_utils.get_param_value(Parameters.PERFORMANCE_DFG, parameters, None))
    frequency_dfg = copy(frequency_dfg)

    artificial_start_activity = exec_utils.get_param_value(Parameters.PARAM_ARTIFICIAL_START_ACTIVITY, parameters, constants.DEFAULT_ARTIFICIAL_START_ACTIVITY)
    artificial_end_activity = exec_utils.get_param_value(Parameters.PARAM_ARTIFICIAL_END_ACTIVITY, parameters, constants.DEFAULT_ARTIFICIAL_END_ACTIVITY)

    for sa in start_activities:
        frequency_dfg[(artificial_start_activity, sa)] = start_activities[sa]
        performance_dfg[(artificial_start_activity, sa)] = 0

    for ea in end_activities:
        frequency_dfg[(ea, artificial_end_activity)] = end_activities[ea]
        performance_dfg[(ea, artificial_end_activity)] = 0

    choices = {}
    for el in frequency_dfg:
        if not el[0] in choices:
            choices[el[0]] = {}
        choices[el[0]][el[1]] = frequency_dfg[el]

    if performance_dfg is None:
        raise Exception(
            "performance DFG simulation requires the Parameters.PERFORMANCE_DFG ('performance_dfg') parameter specification.")

    log = EventLog()
    curr_st = 10000000

    for i in range(num_traces):
        curr_st += case_arrival_rate
        curr_t = curr_st
        trace = Trace(attributes={case_id_key: str(i)})
        log.append(trace)
        curr_act = artificial_start_activity
        while True:
            next_act = dict_based_choice(choices[curr_act])
            if next_act == artificial_end_activity or next_act is None:
                break
            perf = performance_dfg[(curr_act, next_act)]
            if isinstance(perf, dict):
                perf = perf["mean"]
            perf = 0 if perf == 0 else exponential(perf)
            curr_t += perf
            curr_act = next_act
            eve = Event({activity_key: curr_act, timestamp_key: strpfromiso.fix_naivety(datetime.fromtimestamp(curr_t))})
            trace.append(eve)

    return log

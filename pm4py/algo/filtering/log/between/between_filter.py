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
from enum import Enum
from copy import copy
from typing import Optional, Dict, Any, Union, List

from pm4py.objects.log.obj import EventLog, Trace
from pm4py.util import exec_utils, constants, xes_constants
from pm4py.objects.conversion.log import converter as log_converter


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    SUBCASE_CONCAT_STR = "subcase_concat_str"


def __fix_trace_attributes(trace_attributes, idx, rel_count, case_id_key, subcase_concat_str):
    trace_attributes = copy(trace_attributes)
    if case_id_key in trace_attributes:
        trace_attributes[case_id_key] = trace_attributes[case_id_key] + subcase_concat_str + str(rel_count)
    else:
        trace_attributes[case_id_key] = str(idx) + subcase_concat_str + str(rel_count)
    return trace_attributes


def apply(log: EventLog, act1: Union[str, List[str]], act2: Union[str, List[str]], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> EventLog:
    """
    Given an event log, filters all the subtraces going from an event with activity "act1" to an event with
    activity "act2"

    Parameters
    ----------------
    log
        Event log
    act1
        First activity (or collection of activities)
    act2
        Second activity (or collection of activities)
    parameters
        Parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY => activity key

    Returns
    ----------------
    filtered_log
        Log with all the subtraces going from "act1" to "act2"
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, xes_constants.DEFAULT_TRACEID_KEY)
    subcase_concat_str = exec_utils.get_param_value(Parameters.SUBCASE_CONCAT_STR, parameters, "##@@")

    act1_comparison = lambda x: (x == act1) if type(act1) is str else (x in act1)
    act2_comparison = lambda x: (x == act2) if type(act2) is str else (x in act2)

    filtered_log = EventLog(attributes=log.attributes, extensions=log.extensions, omni_present=log.omni_present,
                            classifiers=log.classifiers, properties=log.properties)

    for idx, trace in enumerate(log):
        act1_encountered = False
        filt_trace = None

        rel_count = 0
        i = 0
        while i < len(trace):
            if not act1_encountered and act1_comparison(trace[i][activity_key]):
                act1_encountered = True
                filt_trace = Trace(attributes=__fix_trace_attributes(trace.attributes, idx, rel_count, case_id_key,
                                                                     subcase_concat_str))
                filt_trace.append(trace[i])
            elif act1_encountered and act2_comparison(trace[i][activity_key]):
                filt_trace.append(trace[i])
                filtered_log.append(filt_trace)
                rel_count += 1
                if act1 != act2:
                    # if the between filter is applied between two activities A and B, with A different from B,
                    # then the filter should stop until the next occurrence of A
                    act1_encountered = False
                    filt_trace = None
                else:
                    # otherwise, if A = B, then it continues outputting the events to a new subcase
                    filt_trace = Trace(attributes=__fix_trace_attributes(trace.attributes, idx, rel_count, case_id_key,
                                                                         subcase_concat_str))
                    filt_trace.append(trace[i])

            elif filt_trace is not None:
                filt_trace.append(trace[i])

            i = i + 1

    return filtered_log

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
from pm4py.statistics.attributes.log.get import get_attribute_values, get_all_event_attributes_from_log, get_all_trace_attributes_from_log, get_trace_attribute_values
from pm4py.objects.log.util import sampling
from typing import Union, List, Set
from pm4py.objects.log.obj import EventLog
from pm4py.objects.conversion.log import converter as log_converter


DEFAULT_MAX_CASES_FOR_ATTR_SELECTION = 50


def select_attributes_from_log_for_tree(log: EventLog, max_cases_for_attr_selection=DEFAULT_MAX_CASES_FOR_ATTR_SELECTION,
                                        max_diff_occ=DEFAULT_MAX_CASES_FOR_ATTR_SELECTION / 4):
    """
    Select attributes from log for tree

    Parameters
    ------------
    log
        Log
    max_cases_for_attr_selection
        Maximum number of cases to consider for attribute selection
    max_diff_occ
        Maximum number of different occurrences

    Returns
    ------------

    """
    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG)

    if len(log) > max_cases_for_attr_selection:
        filtered_log = sampling.sample(log, max_cases_for_attr_selection)
    else:
        filtered_log = log
    event_attributes = get_all_event_attributes_from_log(filtered_log)
    trace_attributes = get_all_trace_attributes_from_log(filtered_log)
    event_attributes_values = {}
    trace_attributes_values = {}
    for attr in event_attributes:
        event_attributes_values[attr] = set(get_attribute_values(log, attr).keys())
    for attr in trace_attributes:
        trace_attributes_values[attr] = set(get_trace_attribute_values(log, attr).keys())

    numeric_event_attributes_to_consider = list()
    string_event_attributes_to_consider = list()
    numeric_trace_attributes_to_consider = list()
    string_trace_attributes_to_consider = list()

    for attr in event_attributes_values:
        lst = list(event_attributes_values[attr])
        val = lst[0]
        if type(val) is int or type(val) is float:
            numeric_event_attributes_to_consider.append(attr)
        elif type(val) is str and len(lst) < max_diff_occ:
            string_event_attributes_to_consider.append(attr)

    for attr in trace_attributes_values:
        lst = list(trace_attributes_values[attr])
        val = lst[0]
        if type(val) is int or type(val) is float:
            numeric_trace_attributes_to_consider.append(attr)
        elif type(val) is str and len(lst) < max_diff_occ:
            string_trace_attributes_to_consider.append(attr)

    numeric_event_attributes_to_consider = check_event_attributes_presence(log,
                                                                           numeric_event_attributes_to_consider)
    string_event_attributes_to_consider = check_event_attributes_presence(log,
                                                                          string_event_attributes_to_consider)
    numeric_trace_attributes_to_consider = check_trace_attributes_presence(log,
                                                                           numeric_trace_attributes_to_consider)
    string_trace_attributes_to_consider = check_trace_attributes_presence(log,
                                                                          string_trace_attributes_to_consider)

    return string_trace_attributes_to_consider, string_event_attributes_to_consider, numeric_trace_attributes_to_consider, numeric_event_attributes_to_consider


def check_trace_attributes_presence(log: EventLog, attributes_set: Union[Set[str], List[str]]) -> Union[Set[str], List[str]]:
    """
    Check trace attributes presence in all the traces of the log

    Parameters
    ------------
    log
        Log
    attributes_set
        Set of attributes

    Returns
    ------------
    filtered_set
        Filtered set of attributes
    """
    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG)

    keys = list(attributes_set)
    for attr in keys:
        if not verify_if_trace_attribute_is_in_each_trace(log, attr):
            attributes_set.remove(attr)
    return attributes_set


def check_event_attributes_presence(log: EventLog, attributes_set: Union[Set[str], List[str]]) -> Union[Set[str], List[str]]:
    """
    Check event attributes presence in all the traces of the log

    Parameters
    ------------
    log
        Log
    attributes_set
        Set of attributes

    Returns
    ------------
    filtered_set
        Filtered set of attributes
    """
    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG)

    keys = list(attributes_set)
    for attr in keys:
        if not verify_if_event_attribute_is_in_each_trace(log, attr):
            attributes_set.remove(attr)
    return attributes_set


def verify_if_event_attribute_is_in_each_trace(log: EventLog, attribute: str) -> bool:
    """
    Verify if the event attribute is in each trace

    Parameters
    ------------
    log
        Log
    attribute
        Attribute

    Returns
    ------------
    boolean
        Boolean value that is aiming to check if the event attribute is in each trace
    """
    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG)

    for trace in log:
        present = False
        for event in trace:
            if attribute in event:
                present = True
                break
        if not present:
            return False
    return True


def verify_if_trace_attribute_is_in_each_trace(log: EventLog, attribute: str) -> bool:
    """
    Verify if the trace attribute is in each trace

    Parameters
    -------------
    log
        Log
    attribute
        Attribute

    Returns
    ------------
    boolean
        Boolean value that is aiming to check if the trace attribute is in each trace
    """
    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG)

    for trace in log:
        if attribute not in trace.attributes:
            return False
    return True

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
import numpy as np
from pm4py.util.business_hours import BusinessHours
from pm4py.util import constants

def get_class_representation_by_str_ev_attr_value_presence(log, str_attr_name, str_attr_value):
    """
    Get the representation for the target part of the decision tree learning
    if the focus is on the presence of a given value of a (string) event attribute

    Parameters
    -------------
    log
        Trace log
    str_attr_name
        Attribute name to consider
    str_attr_value
        Attribute value to consider

    Returns
    -------------
    target
        Target part for decision tree learning
    classes
        Name of the classes, in order
    """
    count = 0
    dictionary = {}
    target = []
    classes = []

    for trace in log:
        value = False
        for event in trace:
            if str_attr_name in event and event[str_attr_name] == str_attr_value:
                value = True
        if not str(value) in dictionary:
            dictionary[str(value)] = count
            classes.append(str(value))
            count = count + 1
        target.append(dictionary[str(value)])

    target = np.array(target)
    return target, classes


def get_class_representation_by_str_ev_attr_value_value(log, str_attr_name):
    """
    Get the representation for the target part of the decision tree learning
    if the focus is on all (string) values of an event attribute

    Parameters
    ------------
    log
        Trace log
    str_attr_name
        Attribute name to consider

    Returns
    ------------
    target
        Target part for decision tree learning
    classes
        Name of the classes, in order
    """
    count = 0
    dictionary = {}
    target = []
    classes = []

    for trace in log:
        value = "UNDEFINED"
        for event in trace:
            if str_attr_name in event and event[str_attr_name]:
                value = event[str_attr_name]
        if not str(value) in dictionary:
            dictionary[str(value)] = count
            classes.append(str(value))
            count = count + 1
        target.append(dictionary[str(value)])

    target = np.array(target)
    return target, classes


def get_class_representation_by_trace_duration(log, target_trace_duration, timestamp_key="time:timestamp",
                                               parameters=None):
    """
    Get class representation by splitting traces according to trace duration

    Parameters
    ------------
    log
        Trace log
    target_trace_duration
        Target trace duration
    timestamp_key
        Timestamp key

    Returns
    ------------
    target
        Target part for decision tree learning
    classes
        Name of the classes, in order
    """
    if parameters is None:
        parameters = {}

    business_hours = parameters["business_hours"] if "business_hours" in parameters else False
    business_hours_slots = parameters["business_hour_slots"] if "business_hour_slots" in parameters else constants.DEFAULT_BUSINESS_HOUR_SLOTS

    count = 0
    dictionary = {}
    target = []
    classes = []

    for trace in log:
        value = "LESSEQUAL"
        if len(trace) > 0 and timestamp_key in trace[0] and timestamp_key in trace[-1]:
            timestamp_st = trace[0][timestamp_key]
            timestamp_et = trace[-1][timestamp_key]
            if business_hours:
                bh = BusinessHours(timestamp_st, timestamp_et,
                                   business_hour_slots=business_hours_slots)
                diff = bh.get_seconds()
            else:
                diff = (timestamp_et - timestamp_st).total_seconds()
            if diff > target_trace_duration:
                value = "GREATER"
        if not str(value) in dictionary:
            dictionary[str(value)] = count
            classes.append(str(value))
            count = count + 1
        target.append(dictionary[str(value)])

    target = np.array(target)
    return target, classes

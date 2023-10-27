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

from pm4py.statistics.attributes.log.select import *
from pm4py.statistics.attributes.log.get import *
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.obj import Trace
from pm4py.statistics.attributes.log.get import get_attribute_values
from pm4py.util import exec_utils
from pm4py.util import xes_constants as xes
from pm4py.util.constants import PARAMETER_CONSTANT_ATTRIBUTE_KEY, PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_CASEID_KEY, PARAMETER_KEY_CASE_GLUE
from pm4py.util.xes_constants import DEFAULT_NAME_KEY
from copy import copy
from typing import Optional, Dict, Any, Union, List
from pm4py.objects.log.obj import EventLog, EventStream


class Parameters(Enum):
    ATTRIBUTE_KEY = PARAMETER_CONSTANT_ATTRIBUTE_KEY
    ACTIVITY_KEY = PARAMETER_CONSTANT_ACTIVITY_KEY
    CASE_ID_KEY = PARAMETER_CONSTANT_CASEID_KEY
    PARAMETER_KEY_CASE_GLUE = PARAMETER_KEY_CASE_GLUE
    DECREASING_FACTOR = "decreasingFactor"
    POSITIVE = "positive"
    STREAM_FILTER_KEY1 = "stream_filter_key1"
    STREAM_FILTER_VALUE1 = "stream_filter_value1"
    STREAM_FILTER_KEY2 = "stream_filter_key2"
    STREAM_FILTER_VALUE2 = "stream_filter_value2"
    KEEP_ONCE_PER_CASE = "keep_once_per_case"


def apply_numeric(log: EventLog, int1: float, int2: float, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> EventLog:
    """
    Apply a filter on cases (numerical filter)

    Parameters
    --------------
    log
        Log
    int1
        Lower bound of the interval
    int2
        Upper bound of the interval
    parameters
        Possible parameters of the algorithm

    Returns
    --------------
    filtered_df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    attribute_key = exec_utils.get_param_value(Parameters.ATTRIBUTE_KEY, parameters, DEFAULT_NAME_KEY)
    case_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, xes.DEFAULT_TRACEID_KEY)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)
    case_attribute_prefix = exec_utils.get_param_value(Parameters.PARAMETER_KEY_CASE_GLUE, parameters, constants.CASE_ATTRIBUTE_PREFIX)
    # stream_filter_key is helpful to filter on cases containing an event with an attribute
    # in the specified value set, but such events shall have an activity in particular.

    stream_filter_key1 = exec_utils.get_param_value(Parameters.STREAM_FILTER_KEY1, parameters, None)
    stream_filter_value1 = exec_utils.get_param_value(Parameters.STREAM_FILTER_VALUE1, parameters, None)
    stream_filter_key2 = exec_utils.get_param_value(Parameters.STREAM_FILTER_KEY2, parameters, None)
    stream_filter_value2 = exec_utils.get_param_value(Parameters.STREAM_FILTER_VALUE2, parameters, None)

    conversion_parameters = copy(parameters)
    conversion_parameters["deepcopy"] = False

    stream = log_converter.apply(log, variant=log_converter.TO_EVENT_STREAM, parameters=conversion_parameters)
    if stream_filter_key1 is not None:
        stream = EventStream(
            list(filter(lambda x: stream_filter_key1 in x and x[stream_filter_key1] == stream_filter_value1, stream)),
            attributes=log.attributes, extensions=log.extensions, classifiers=log.classifiers,
            omni_present=log.omni_present, properties=log.properties)
    if stream_filter_key2 is not None:
        stream = EventStream(
            list(filter(lambda x: stream_filter_key2 in x and x[stream_filter_key2] == stream_filter_value2, stream)),
            attributes=log.attributes, extensions=log.extensions, classifiers=log.classifiers,
            omni_present=log.omni_present, properties=log.properties)

    if positive:
        stream = EventStream(list(filter(lambda x: attribute_key in x and int1 <= x[attribute_key] <= int2, stream)),
                             attributes=log.attributes, extensions=log.extensions, classifiers=log.classifiers,
                             omni_present=log.omni_present, properties=log.properties)
    else:
        stream = EventStream(
            list(filter(lambda x: attribute_key in x and (x[attribute_key] < int1 or x[attribute_key] > int2), stream)),
            attributes=log.attributes, extensions=log.extensions, classifiers=log.classifiers,
            omni_present=log.omni_present, properties=log.properties)

    all_cases_ids = set(x[case_attribute_prefix + case_key] for x in stream)

    filtered_log = EventLog(list(), attributes=log.attributes, extensions=log.extensions, classifiers=log.classifiers,
                            omni_present=log.omni_present, properties=log.properties)

    for case in log:
        if case.attributes[case_key] in all_cases_ids:
            filtered_log.append(case)

    return filtered_log


def apply_numeric_events(log: EventLog, int1: float, int2: float, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> EventLog:
    """
    Apply a filter on events (numerical filter)

    Parameters
    --------------
    log
        Log
    int1
        Lower bound of the interval
    int2
        Upper bound of the interval
    parameters
        Possible parameters of the algorithm:
            Parameters.ATTRIBUTE_KEY => indicates which attribute to filter
            Parameters.POSITIVE => keep or remove traces with such events?

    Returns
    --------------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    attribute_key = exec_utils.get_param_value(Parameters.ATTRIBUTE_KEY, parameters, DEFAULT_NAME_KEY)

    conversion_parameters = copy(parameters)
    conversion_parameters["deepcopy"] = False
    stream = log_converter.apply(log, variant=log_converter.TO_EVENT_STREAM, parameters=conversion_parameters)
    if exec_utils.get_param_value(Parameters.POSITIVE, parameters, True):
        stream = EventStream(list(filter(lambda x: attribute_key in x and int1 <= x[attribute_key] <= int2, stream)),
                             attributes=log.attributes, extensions=log.extensions, classifiers=log.classifiers,
                             omni_present=log.omni_present, properties=log.properties)
    else:
        stream = EventStream(
            list(filter(lambda x: attribute_key in x and (x[attribute_key] < int1 or x[attribute_key] > int2), stream)),
            attributes=log.attributes, extensions=log.extensions, classifiers=log.classifiers,
            omni_present=log.omni_present, properties=log.properties)
    filtered_log = log_converter.apply(stream, variant=log_converter.Variants.TO_EVENT_LOG, parameters=conversion_parameters)

    return filtered_log


def apply_events(log: EventLog, values: List[str], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> EventLog:
    """
    Filter log by keeping only events with an attribute value that belongs to the provided values list

    Parameters
    -----------
    log
        log
    values
        Allowed attributes
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> Attribute identifying the activity in the log
            Parameters.POSITIVE -> Indicate if events should be kept/removed

    Returns
    -----------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    attribute_key = exec_utils.get_param_value(Parameters.ATTRIBUTE_KEY, parameters, DEFAULT_NAME_KEY)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)

    conversion_parameters = copy(parameters)
    conversion_parameters["deepcopy"] = False

    stream = log_converter.apply(log, variant=log_converter.TO_EVENT_STREAM, parameters=conversion_parameters)
    if positive:
        stream = EventStream(list(filter(lambda x: x[attribute_key] in values, stream)), attributes=log.attributes,
                             extensions=log.extensions, classifiers=log.classifiers,
                             omni_present=log.omni_present, properties=log.properties)
    else:
        stream = EventStream(list(filter(lambda x: x[attribute_key] not in values, stream)), attributes=log.attributes,
                             extensions=log.extensions, classifiers=log.classifiers,
                             omni_present=log.omni_present, properties=log.properties)

    filtered_log = log_converter.apply(stream, variant=log_converter.Variants.TO_EVENT_LOG, parameters=conversion_parameters)

    return filtered_log


def apply(log: EventLog, values: List[str], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> EventLog:
    """
    Filter log by keeping only traces that has/has not events with an attribute value that belongs to the provided
    values list

    Parameters
    -----------
    log
        Trace log
    values
        Allowed attributes
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> Attribute identifying the activity in the log
            Parameters.POSITIVE -> Indicate if events should be kept/removed

    Returns
    -----------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    attribute_key = exec_utils.get_param_value(Parameters.ATTRIBUTE_KEY, parameters, DEFAULT_NAME_KEY)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)

    filtered_log = EventLog(list(), attributes=log.attributes, extensions=log.extensions, classifiers=log.classifiers,
                            omni_present=log.omni_present, properties=log.properties)
    for trace in log:
        new_trace = Trace()

        found = False
        for j in range(len(trace)):
            if attribute_key in trace[j]:
                attribute_value = trace[j][attribute_key]
                if attribute_value in values:
                    found = True

        if (found and positive) or (not found and not positive):
            new_trace = trace
        else:
            for attr in trace.attributes:
                new_trace.attributes[attr] = trace.attributes[attr]

        if len(new_trace) > 0:
            filtered_log.append(new_trace)
    return filtered_log


def apply_trace_attribute(log: EventLog, values: List[str], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> EventLog:
    """
    Filter a log on the trace attribute values

    Parameters
    --------------
    log
        Event log
    values
        Allowed/forbidden values
    parameters
        Parameters of the algorithm, including:
            - Parameters.ATTRIBUTE_KEY: the attribute at the trace level to filter
            - Parameters.POSITIVE: boolean (keep/discard values)

    Returns
    --------------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    attribute_key = exec_utils.get_param_value(Parameters.ATTRIBUTE_KEY, parameters, DEFAULT_NAME_KEY)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)

    filtered_log = EventLog(list(), attributes=log.attributes, extensions=log.extensions, classifiers=log.classifiers,
                            omni_present=log.omni_present, properties=log.properties)
    for trace in log:
        if positive:
            if attribute_key in trace.attributes and trace.attributes[attribute_key] in values:
                filtered_log.append(trace)
        else:
            if not attribute_key in trace.attributes or not trace.attributes[attribute_key] in values:
                filtered_log.append(trace)

    return filtered_log


def filter_log_on_max_no_activities(log: EventLog, max_no_activities : int = 25, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> EventLog:
    """
    Filter a log on a maximum number of activities

    Parameters
    -------------
    log
        Log
    max_no_activities
        Maximum number of activities
    parameters
        Parameters of the algorithm

    Returns
    -------------
    filtered_log
        Filtered version of the event log
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    activity_key = parameters[
        PARAMETER_CONSTANT_ACTIVITY_KEY] if PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else DEFAULT_NAME_KEY
    parameters[PARAMETER_CONSTANT_ATTRIBUTE_KEY] = activity_key
    all_activities = sorted([(x, y) for x, y in get_attribute_values(log, activity_key).items()], key=lambda x: x[1],
                            reverse=True)
    activities = all_activities[:min(len(all_activities), max_no_activities)]
    activities = [x[0] for x in activities]

    if len(activities) < len(all_activities):
        log = apply_events(log, activities, parameters=parameters)
    return log


def filter_log_by_attributes_threshold(log, attributes, variants, vc, threshold, attribute_key=xes.DEFAULT_NAME_KEY):
    """
    Keep only attributes which number of occurrences is above the threshold (or they belong to the first variant)

    Parameters
    ----------
    log
        Log
    attributes
        Dictionary of attributes associated with their count
    variants
        (If specified) Dictionary with variant as the key and the list of traces as the value
    vc
        List of variant names along with their count
    threshold
        Cutting threshold (remove attributes which number of occurrences is below the threshold)
    attribute_key
        (If specified) Specify the activity key in the log (default concept:name)

    Returns
    ----------
    filtered_log
        Filtered log
    """
    filtered_log = EventLog(list(), attributes=log.attributes, extensions=log.extensions, classifiers=log.classifiers,
                            omni_present=log.omni_present, properties=log.properties)
    fva = [x[attribute_key] for x in variants[vc[0][0]][0] if attribute_key in x]
    for trace in log:
        new_trace = Trace()
        for j in range(len(trace)):
            if attribute_key in trace[j]:
                attribute_value = trace[j][attribute_key]
                if attribute_value in attributes:
                    if (attribute_value in fva and attribute_key == xes.DEFAULT_NAME_KEY) or attributes[
                        attribute_value] >= threshold:
                        new_trace.append(trace[j])
        if len(new_trace) > 0:
            for attr in trace.attributes:
                new_trace.attributes[attr] = trace.attributes[attr]
            filtered_log.append(new_trace)
    return filtered_log


def filter_log_relative_occurrence_event_attribute(log: EventLog, min_relative_stake: float, parameters: Optional[Dict[Any, Any]] = None) -> EventLog:
    """
    Filters the event log keeping only the events having an attribute value which occurs:
    - in at least the specified (min_relative_stake) percentage of events, when Parameters.KEEP_ONCE_PER_CASE = False
    - in at least the specified (min_relative_stake) percentage of cases, when Parameters.KEEP_ONCE_PER_CASE = True

    Parameters
    -------------------
    log
        Event log
    min_relative_stake
        Minimum percentage of cases (expressed as a number between 0 and 1) in which the attribute should occur.
    parameters
        Parameters of the algorithm, including:
        - Parameters.ATTRIBUTE_KEY => the attribute to use (default: concept:name)
        - Parameters.KEEP_ONCE_PER_CASE => decides the level of the filter to apply
        (if the filter should be applied on the cases, set it to True).

    Returns
    ------------------
    filtered_log
        Filtered event log
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    attribute_key = exec_utils.get_param_value(Parameters.ATTRIBUTE_KEY, parameters, xes.DEFAULT_NAME_KEY)
    keep_once_per_case = exec_utils.get_param_value(Parameters.KEEP_ONCE_PER_CASE, parameters, True)

    parameters_cp = copy(parameters)

    activities_occurrences = get_attribute_values(log, attribute_key, parameters=parameters_cp)

    if keep_once_per_case:
        # filter on cases
        filtered_attributes = set(x for x, y in activities_occurrences.items() if y >= min_relative_stake * len(log))
    else:
        # filter on events
        filtered_attributes = set(x for x, y in activities_occurrences.items() if y >= min_relative_stake * sum(len(x) for x in log))

    return apply_events(log, filtered_attributes, parameters=parameters)

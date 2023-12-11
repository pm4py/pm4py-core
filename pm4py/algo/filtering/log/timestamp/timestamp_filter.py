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
import datetime
from enum import Enum

from pm4py.algo.filtering.common.timestamp.timestamp_common import get_dt_from_string
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.obj import Trace
from pm4py.util import exec_utils
from pm4py.util.constants import PARAMETER_CONSTANT_TIMESTAMP_KEY
from pm4py.util.xes_constants import DEFAULT_TIMESTAMP_KEY

from typing import Optional, Dict, Any, Union
from pm4py.objects.log.obj import EventLog, EventStream
from pm4py.util.dt_parsing.variants import strpfromiso


class Parameters(Enum):
    TIMESTAMP_KEY = PARAMETER_CONSTANT_TIMESTAMP_KEY


def trace_attr_is_contained(trace: Trace, dt1: Union[str, datetime.datetime], dt2: Union[str, datetime.datetime],
                            trace_attr: str) -> bool:
    """
    Checks if the given attribute at the trace level is contained in the provided range

    Parameters
    ----------------
    trace
        Trace object
    dt1
        Left extreme of the time interval
    dt2
        Right extreme of the time interval
    trace_attr
        Attribute at the trace level that is considered for the filtering

    Returns
    ----------------
    boolean
        Boolean value
    """
    if trace_attr in trace.attributes:
        if dt1 <= strpfromiso.fix_naivety(trace.attributes[trace_attr]) <= dt2:
            return True
    return False


def filter_on_trace_attribute(log: EventLog, dt1: Union[str, datetime.datetime], dt2: Union[str, datetime.datetime],
                              parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> EventLog:
    """
    Filters the traces of the event log that have a given trace attribute
    falling in the provided range

    Parameters
    -----------------
    log
        Event log
    dt1
        Left extreme of the time interval
    dt2
        Right extreme of the time interval
    parameters
        Parameters of the filtering, including:
        - Parameters.TIMESTAMP_KEY => trace attribute to use for the filtering

    Returns
    ------------------
    filtered_log
        Filtered event log
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    trace_attribute = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY)
    dt1 = get_dt_from_string(dt1)
    dt2 = get_dt_from_string(dt2)
    filtered_log = EventLog([trace for trace in log if trace_attr_is_contained(trace, dt1, dt2, trace_attribute)],
                            attributes=log.attributes, extensions=log.extensions, omni_present=log.omni_present,
                            classifiers=log.classifiers, properties=log.properties)
    return filtered_log


def is_contained(trace, dt1, dt2, timestamp_key):
    """
    Check if a trace is contained in the given interval

    Parameters
    -----------
    trace
        Trace to check
    dt1
        Lower bound to the interval
    dt2
        Upper bound to the interval
    timestamp_key
        Timestamp attribute

    Returns
    -----------
    boolean
        Is true if the trace is contained
    """
    if trace:
        if strpfromiso.fix_naivety(trace[0][timestamp_key]) >= dt1 and strpfromiso.fix_naivety(trace[-1][timestamp_key]) <= dt2:
            return True
    return False


def filter_traces_contained(log: EventLog, dt1: Union[str, datetime.datetime], dt2: Union[str, datetime.datetime], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> EventLog:
    """
    Get traces that are contained in the given interval

    Parameters
    -----------
    log
        Trace log
    dt1
        Lower bound to the interval
    dt2
        Upper bound to the interval
    parameters
        Possible parameters of the algorithm, including:
            Parameters.TIMESTAMP_KEY -> Attribute to use as timestamp

    Returns
    ------------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY)
    dt1 = get_dt_from_string(dt1)
    dt2 = get_dt_from_string(dt2)
    filtered_log = EventLog([trace for trace in log if is_contained(trace, dt1, dt2, timestamp_key)],
                            attributes=log.attributes, extensions=log.extensions, omni_present=log.omni_present,
                            classifiers=log.classifiers, properties=log.properties)
    return filtered_log


def is_intersecting(trace, dt1, dt2, timestamp_key):
    """
    Check if a trace is intersecting in the given interval

    Parameters
    -----------
    trace
        Trace to check
    dt1
        Lower bound to the interval
    dt2
        Upper bound to the interval
    timestamp_key
        Timestamp attribute

    Returns
    -----------
    boolean
        Is true if the trace is contained
    """
    if trace:
        condition1 = dt1 <= strpfromiso.fix_naivety(trace[0][timestamp_key]) <= dt2
        condition2 = dt1 <= strpfromiso.fix_naivety(trace[-1][timestamp_key]) <= dt2
        condition3 = strpfromiso.fix_naivety(trace[0][timestamp_key]) <= dt1 <= strpfromiso.fix_naivety(trace[-1][timestamp_key])
        condition4 = strpfromiso.fix_naivety(trace[0][timestamp_key]) <= dt2 <= strpfromiso.fix_naivety(trace[-1][timestamp_key])

        if condition1 or condition2 or condition3 or condition4:
            return True
    return False


def filter_traces_intersecting(log: EventLog, dt1: Union[str, datetime.datetime], dt2: Union[str, datetime.datetime], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> EventLog:
    """
    Filter traces intersecting the given interval

    Parameters
    -----------
    log
        Trace log
    dt1
        Lower bound to the interval
    dt2
        Upper bound to the interval
    parameters
        Possible parameters of the algorithm, including:
            Parameters.TIMESTAMP_KEY -> Attribute to use as timestamp

    Returns
    ------------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    timestamp_key = parameters[
        PARAMETER_CONSTANT_TIMESTAMP_KEY] if PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else DEFAULT_TIMESTAMP_KEY
    dt1 = get_dt_from_string(dt1)
    dt2 = get_dt_from_string(dt2)
    filtered_log = EventLog([trace for trace in log if is_intersecting(trace, dt1, dt2, timestamp_key)],
                            attributes=log.attributes, extensions=log.extensions, omni_present=log.omni_present,
                            classifiers=log.classifiers, properties=log.properties)
    return filtered_log


def apply_events(log: EventLog, dt1: Union[str, datetime.datetime], dt2: Union[str, datetime.datetime], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> EventLog:
    """
    Get a new log containing all the events contained in the given interval

    Parameters
    -----------
    log
        Log
    dt1
        Lower bound to the interval
    dt2
        Upper bound to the interval
    parameters
        Possible parameters of the algorithm, including:
            Parameters.TIMESTAMP_KEY -> Attribute to use as timestamp

    Returns
    ------------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY)
    dt1 = get_dt_from_string(dt1)
    dt2 = get_dt_from_string(dt2)

    stream = log_converter.apply(log, variant=log_converter.TO_EVENT_STREAM, parameters={"deepcopy": False})
    filtered_stream = EventStream([x for x in stream if dt1 <= strpfromiso.fix_naivety(x[timestamp_key]) <= dt2],
                                  attributes=log.attributes, extensions=log.extensions, omni_present=log.omni_present,
                                  classifiers=log.classifiers, properties=log.properties)
    filtered_log = log_converter.apply(filtered_stream, variant=log_converter.Variants.TO_EVENT_LOG)

    return filtered_log


def has_attribute_in_timeframe(trace, attribute, attribute_value, dt1, dt2, timestamp_key):
    for e in trace:
        if attribute in e and e[attribute] == attribute_value and dt1 <= strpfromiso.fix_naivety(e[timestamp_key]) <= dt2:
            return True
    return False


def filter_traces_attribute_in_timeframe(log: EventLog, attribute: str, attribute_value: Any, dt1: Union[str, datetime.datetime], dt2: Union[str, datetime.datetime], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> EventLog:
    """
    Get a new log containing all the traces that have an event in the given interval with the specified attribute value 

    Parameters
    -----------
    log
        Log
    attribute
        The attribute to filter on
    attribute_value
        The attribute value to filter on
    dt1
        Lower bound to the interval
    dt2
        Upper bound to the interval
    parameters
        Possible parameters of the algorithm, including:
            Parameters.TIMESTAMP_KEY -> Attribute to use as timestamp

    Returns
    ------------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY)
    dt1 = get_dt_from_string(dt1)
    dt2 = get_dt_from_string(dt2)

    filtered_log = EventLog([trace for trace in log if
                             has_attribute_in_timeframe(trace, attribute, attribute_value, dt1, dt2, timestamp_key)],
                            attributes=log.attributes, extensions=log.extensions, omni_present=log.omni_present,
                            classifiers=log.classifiers)
    return filtered_log


def apply(df, parameters=None):
    del df
    del parameters
    raise Exception("apply method not available for timestamp filter")


def apply_auto_filter(df, parameters=None):
    del df
    del parameters
    raise Exception("apply_auto_filter method not available for timestamp filter")

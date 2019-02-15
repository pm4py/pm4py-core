from pm4py.algo.filtering.common.timestamp.timestamp_common import get_dt_from_string
from pm4py.objects.conversion.log import factory as log_converter
from pm4py.objects.log.log import EventLog, EventStream
from pm4py.objects.log.util.xes import DEFAULT_TIMESTAMP_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_TIMESTAMP_KEY


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
        if trace[0][timestamp_key].replace(tzinfo=None) > dt1 and trace[-1][timestamp_key].replace(tzinfo=None) < dt2:
            return True
    return False


def filter_traces_contained(log, dt1, dt2, parameters=None):
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
            timestamp_key -> Attribute to use as timestamp

    Returns
    ------------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}
    timestamp_key = parameters[
        PARAMETER_CONSTANT_TIMESTAMP_KEY] if PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else DEFAULT_TIMESTAMP_KEY
    dt1 = get_dt_from_string(dt1)
    dt2 = get_dt_from_string(dt2)
    filtered_log = EventLog([trace for trace in log if is_contained(trace, dt1, dt2, timestamp_key)])
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
        condition1 = dt1 < trace[0][timestamp_key].replace(tzinfo=None) < dt2
        condition2 = dt1 < trace[-1][timestamp_key].replace(tzinfo=None) < dt2
        condition3 = trace[0][timestamp_key].replace(tzinfo=None) < dt1 < trace[-1][timestamp_key].replace(tzinfo=None)
        condition4 = trace[0][timestamp_key].replace(tzinfo=None) < dt2 < trace[-1][timestamp_key].replace(tzinfo=None)

        if condition1 or condition2 or condition3 or condition4:
            return True
    return False


def filter_traces_intersecting(log, dt1, dt2, parameters=None):
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
            timestamp_key -> Attribute to use as timestamp

    Returns
    ------------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}
    timestamp_key = parameters[
        PARAMETER_CONSTANT_TIMESTAMP_KEY] if PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else DEFAULT_TIMESTAMP_KEY
    dt1 = get_dt_from_string(dt1)
    dt2 = get_dt_from_string(dt2)
    filtered_log = EventLog([trace for trace in log if is_intersecting(trace, dt1, dt2, timestamp_key)])
    return filtered_log


def apply_events(log, dt1, dt2, parameters=None):
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
            timestamp_key -> Attribute to use as timestamp

    Returns
    ------------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}
    timestamp_key = parameters[
        PARAMETER_CONSTANT_TIMESTAMP_KEY] if PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else DEFAULT_TIMESTAMP_KEY
    dt1 = get_dt_from_string(dt1)
    dt2 = get_dt_from_string(dt2)

    stream = log_converter.apply(log, variant=log_converter.TO_EVENT_STREAM)
    filtered_stream = EventStream([x for x in stream if dt1 < x[timestamp_key].replace(tzinfo=None) < dt2])
    filtered_log = log_converter.apply(filtered_stream)

    return filtered_log


def apply(df, parameters=None):
    del df
    del parameters
    raise Exception("apply method not available for timestamp filter")


def apply_auto_filter(df, parameters=None):
    del df
    del parameters
    raise Exception("apply_auto_filter method not available for timestamp filter")

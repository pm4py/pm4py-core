from datetime import datetime
from pm4py.entities.log.log import TraceLog, EventLog
from pm4py.entities.log import transform
from pm4py.entities.log.util import xes
from pm4py.util import constants

def get_dt_from_string(dt):
    """
    If the date is expressed as string, do the conversion to a datetime.datetime object

    Parameters
    -----------
    dt
        Date (string or datetime.datetime)

    Returns
    -----------
    dt
        Datetime object
    """
    if type(dt) is str:
        return datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")

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
    timestamp_key
        Timestamp attribute

    Returns
    ------------
    filtered_log
        Filtered trace log
    """
    if parameters is None:
        parameters = {}
    timestamp_key = parameters[constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] if constants.PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else xes.DEFAULT_TIMESTAMP_KEY
    dt1 = get_dt_from_string(dt1)
    dt2 = get_dt_from_string(dt2)
    filtered_log = TraceLog([trace for trace in log if is_contained(trace, dt1, dt2, timestamp_key)])
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
        condition1 = trace[0][timestamp_key].replace(tzinfo=None) > dt1 and trace[0][timestamp_key].replace(tzinfo=None) < dt2
        condition2 = trace[-1][timestamp_key].replace(tzinfo=None) > dt1 and trace[-1][timestamp_key].replace(tzinfo=None) < dt2
        condition3 = trace[0][timestamp_key].replace(tzinfo=None) < dt1 and trace[0][timestamp_key].replace(tzinfo=None) > dt2

        if condition1 or condition2 or condition3:
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
    timestamp_key
        Timestamp attribute

    Returns
    ------------
    filtered_log
        Filtered trace log
    """
    if parameters is None:
        parameters = {}
    timestamp_key = parameters[
        constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] if constants.PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else xes.DEFAULT_TIMESTAMP_KEY
    dt1 = get_dt_from_string(dt1)
    dt2 = get_dt_from_string(dt2)
    filtered_log = TraceLog([trace for trace in log if is_intersecting(trace, dt1, dt2, timestamp_key)])
    return filtered_log

def filter_events(trace_log, dt1, dt2, parameters=None):
    """
    Get a new trace log containing all the events contained in the given interval

    Parameters
    -----------
    log
        Trace log
    dt1
        Lower bound to the interval
    dt2
        Upper bound to the interval
    timestamp_key
        Timestamp attribute

    Returns
    ------------
    filtered_log
        Filtered trace log
    """
    if parameters is None:
        parameters = {}
    timestamp_key = parameters[
        constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] if constants.PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else xes.DEFAULT_TIMESTAMP_KEY
    dt1 = get_dt_from_string(dt1)
    dt2 = get_dt_from_string(dt2)

    event_log = transform.transform_trace_log_to_event_log(trace_log)
    filtered_event_log = EventLog([x for x in event_log if x[timestamp_key].replace(tzinfo=None) > dt1 and x[timestamp_key].replace(tzinfo=None) < dt2])
    filtered_trace_log = transform.transform_event_log_to_trace_log(filtered_event_log)

    return filtered_trace_log
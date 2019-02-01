from pm4py.objects.log.log import EventLog
from pm4py.objects.log.util.xes import DEFAULT_TIMESTAMP_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_TIMESTAMP_KEY


def filter_on_case_performance(log, inf_perf, sup_perf, parameters=None):
    """
    Gets a filtered log keeping only traces that satisfy the given performance requirements

    Parameters
    ------------
    log
        Log
    inf_perf
        Lower bound on the performance
    sup_perf
        Upper bound on the performance
    parameters
        Parameters

    Returns
    -----------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}
    timestamp_key = parameters[
        PARAMETER_CONSTANT_TIMESTAMP_KEY] if PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else DEFAULT_TIMESTAMP_KEY
    filtered_log = EventLog([trace for trace in log if satisfy_perf(trace, inf_perf, sup_perf, timestamp_key)])
    return filtered_log


def filter_on_ncases(log, max_no_cases=1000):
    """
    Get only a specified number of traces from a log

    Parameters
    -----------
    log
        Log
    max_no_cases
        Desidered number of traces from the log

    Returns
    -----------
    filtered_log
        Filtered log
    """
    filtered_log = EventLog(log[:min(len(log), max_no_cases)])
    return filtered_log


def filter_on_case_size(log, min_case_size=2, max_case_size=None):
    """
    Get only traces in the log with a given size

    Parameters
    -----------
    log
        Log
    min_case_size
        Minimum desidered size of traces
    max_case_size
        Maximum desidered size of traces

    Returns
    -----------
    filtered_log
        Filtered log
    """
    if max_case_size is not None:
        filtered_log = EventLog([trace for trace in log if min_case_size <= len(trace) <= max_case_size])
    else:
        filtered_log = EventLog([trace for trace in log if len(trace) >= min_case_size])
    return filtered_log


def satisfy_perf(trace, inf_perf, sup_perf, timestamp_key):
    """
    Checks if the trace satisfy the performance requirements

    Parameters
    -----------
    trace
        Trace
    inf_perf
        Lower bound on the performance
    sup_perf
        Upper bound on the performance
    timestamp_key
        Timestamp key

    Returns
    -----------
    boolean
        Boolean (is True if the trace satisfy the given performance requirements)
    """
    if trace:
        trace_duration = (trace[-1][timestamp_key] - trace[0][timestamp_key]).total_seconds()
        return inf_perf <= trace_duration <= sup_perf
    return False


def apply(df, parameters=None):
    del df
    del parameters
    raise NotImplementedError("apply method not available for case filter")


def apply_auto_filter(df, parameters=None):
    del df
    del parameters
    raise NotImplementedError("apply_auto_filter method not available for case filter")

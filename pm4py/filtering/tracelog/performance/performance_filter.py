from pm4py.entities.log.log import TraceLog
from pm4py.entities.log.util import xes
from pm4py.util import constants

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
        if trace_duration >= inf_perf and trace_duration <= sup_perf:
            return True
    return False

def filter_traces_by_performance(trace_log, inf_perf, sup_perf, parameters=None):
    """
    Gets a filtered trace log keeping only traces that satisfy the given performance requirements

    Parameters
    ------------
    trace_log
        Trace log
    inf_perf
        Lower bound on the performance
    sup_perf
        Upper bound on the performance
    parameters
        Parameters

    Returns
    -----------
    filtered_log
        Filtered trace log
    """
    if parameters is None:
        parameters = {}
    timestamp_key = parameters[
        constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] if constants.PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else xes.DEFAULT_TIMESTAMP_KEY
    filtered_log = TraceLog([trace for trace in trace_log if satisfy_perf(trace, inf_perf, sup_perf, timestamp_key)])
    return filtered_log
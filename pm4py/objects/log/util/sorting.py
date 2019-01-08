from copy import deepcopy

from pm4py.objects.log.log import TraceLog
from pm4py.objects.log.util import xes


def sort_trace(trace, timestamp_key=xes.DEFAULT_TIMESTAMP_KEY, reverse_sort=False):
    """
    Sort a trace based on timestamp key

    Parameters
    -----------
    trace
        Trace
    timestamp_key
        Timestamp key
    reverse_sort
        If true, reverses the direction in which the sort is done (ascending)
    """
    new_trace = deepcopy(trace)
    new_trace._list.sort(key=lambda x: x[timestamp_key], reverse=reverse_sort)
    return new_trace


def sort_eventlog(event_log, timestamp_key=xes.DEFAULT_TIMESTAMP_KEY, reverse_sort=False):
    """
    Sort an event log based on timestamp key

    Parameters
    -----------
    event_log
        Event log
    timestamp_key
        Timestamp key
    reverse_sort
        If true, reverses the direction in which the sort is done (ascending)
    """
    new_event_log = deepcopy(event_log)
    new_event_log._list.sort(key=lambda x: x[timestamp_key], reverse=reverse_sort)
    return new_event_log


def sort_tracelog(trace_log, timestamp_key=xes.DEFAULT_TIMESTAMP_KEY, reverse_sort=False):
    """
    Sort a trace log based on timestamp key

    Parameters
    -----------
    trace_log
        Trace log
    timestamp_key
        Timestamp key
    reverse_sort
        If true, reverses the direction in which the sort is done (ascending)
    """
    new_trace_log = deepcopy(trace_log)
    new_trace_log._list = [x for x in new_trace_log._list if len(x) > 0]
    for i in range(len(new_trace_log._list)):
        new_trace_log._list[i] = sort_trace(new_trace_log._list[i], timestamp_key=timestamp_key,
                                            reverse_sort=reverse_sort)

    new_trace_log._list.sort(key=lambda x: x[0][timestamp_key], reverse=reverse_sort)

    return new_trace_log


def sort(log, timestamp_key=xes.DEFAULT_TIMESTAMP_KEY, reverse_sort=False):
    """
    Sort a log based on timestamp key

    Parameters
    -----------
    log
        Trace/Event log
    timestamp_key
        Timestamp key
    reverse_sort
        If true, reverses the direction in which the sort is done (ascending)
    """

    if type(log) is TraceLog:
        return sort_tracelog(log, timestamp_key=timestamp_key, reverse_sort=reverse_sort)
    return sort_eventlog(log, timestamp_key=timestamp_key, reverse_sort=reverse_sort)

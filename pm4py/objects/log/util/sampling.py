import random
from copy import copy

from pm4py.objects.log.log import EventLog, TraceLog


def sample_eventlog(event_log, no_events=100):
    """
    Randomly sample a fixed number of events from the original event log

    Parameters
    -----------
    event_log
        Event log
    no_events
        Number of events that the sample should have

    Returns
    -----------
    newLog
        Filtered log
    """
    new_log = EventLog(attributes=event_log.attributes, extensions=event_log.extensions, globals=event_log._omni,
                       classifiers=event_log.classifiers)
    set_events = set()
    for i in range(0, min(no_events, len(event_log._list))):
        set_events.add(random.randrange(0, len(event_log._list)))
    set_events = list(set_events)
    for event in set_events:
        new_log.append(copy(event_log._list[event]))
    return new_log


def sample_tracelog(trace_log, no_traces=100):
    """
    Randomly sample a fixed number of traces from the original log

    Parameters
    -----------
    trace_log
        Trace log
    no_traces
        Number of traces that the sample should have

    Returns
    -----------
    newLog
        Filtered log
    """
    new_log = TraceLog(attributes=trace_log.attributes, extensions=trace_log.extensions, globals=trace_log._omni,
                       classifiers=trace_log.classifiers)
    set_traces = set()
    for i in range(0, min(no_traces, len(trace_log._list))):
        set_traces.add(random.randrange(0, len(trace_log._list)))
    set_traces = list(set_traces)
    for trace in set_traces:
        new_log.append(copy(trace_log._list[trace]))
    return new_log


def sample(log, n=100):
    """
    Randomly sample a fixed number of traces from the original log

    Parameters
    -----------
    log
        Trace/event log
    n
        Number of elements that the sample should have

    Returns
    -----------
    newLog
        Filtered log
    """

    if type(log) is TraceLog:
        return sample_tracelog(log, no_traces=n)

    return sample_eventlog(log, no_events=n)

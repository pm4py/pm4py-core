import random
from copy import copy

from pm4py.objects.log.log import EventStream, EventLog


def sample_stream(event_log, no_events=100):
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
    new_log = EventStream(attributes=event_log.attributes, extensions=event_log.extensions, globals=event_log._omni,
                          classifiers=event_log.classifiers)
    new_log._list = random.sample(event_log, min(no_events, len(event_log)))
    return new_log


def sample_log(log, no_traces=100):
    """
    Randomly sample a fixed number of traces from the original log

    Parameters
    -----------
    log
        Log
    no_traces
        Number of traces that the sample should have

    Returns
    -----------
    newLog
        Filtered log
    """
    new_log = EventLog(attributes=log.attributes, extensions=log.extensions, globals=log._omni,
                       classifiers=log.classifiers)
    new_log._list = random.sample(log, min(no_traces, len(log)))
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

    if type(log) is EventLog:
        return sample_log(log, no_traces=n)

    return sample_stream(log, no_events=n)

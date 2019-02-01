from copy import deepcopy

from pm4py.objects.log.log import EventLog
from pm4py.objects.log.util import xes


def sort_timestamp_trace(trace, timestamp_key=xes.DEFAULT_TIMESTAMP_KEY, reverse_sort=False):
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

    Returns
    -----------
    trace
        Sorted trace
    """
    new_trace = deepcopy(trace)
    new_trace._list.sort(key=lambda x: x[timestamp_key], reverse=reverse_sort)
    return new_trace


def sort_timestamp_stream(event_log, timestamp_key=xes.DEFAULT_TIMESTAMP_KEY, reverse_sort=False):
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

    Returns
    -----------
    event_log
        Sorted event log
    """
    new_event_log = deepcopy(event_log)
    new_event_log._list.sort(key=lambda x: x[timestamp_key], reverse=reverse_sort)
    return new_event_log


def sort_timestamp_log(log, timestamp_key=xes.DEFAULT_TIMESTAMP_KEY, reverse_sort=False):
    """
    Sort a log based on timestamp key

    Parameters
    -----------
    log
        Log
    timestamp_key
        Timestamp key
    reverse_sort
        If true, reverses the direction in which the sort is done (ascending)

    Returns
    -----------
    log
        Sorted log
    """
    new_log = deepcopy(log)
    new_log._list = [x for x in new_log._list if len(x) > 0]
    for i in range(len(new_log._list)):
        new_log._list[i] = sort_timestamp_trace(new_log._list[i], timestamp_key=timestamp_key,
                                                      reverse_sort=reverse_sort)

    new_log._list.sort(key=lambda x: x[0][timestamp_key], reverse=reverse_sort)

    return new_log


def sort_timestamp(log, timestamp_key=xes.DEFAULT_TIMESTAMP_KEY, reverse_sort=False):
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

    Returns
    -----------
    log
        Sorted Trace/Event log
    """
    if type(log) is EventLog:
        return sort_timestamp_log(log, timestamp_key=timestamp_key, reverse_sort=reverse_sort)
    return sort_timestamp_stream(log, timestamp_key=timestamp_key, reverse_sort=reverse_sort)


def sort_lambda_log(log, sort_function, reverse=False):
    """
    Sort a log based on a lambda expression

    Parameters
    ------------
    log
        Log
    sort_function
        Sort function
    reverse
        Boolean (sort by reverse order)

    Returns
    ------------
    new_log
        Sorted log
    """
    new_log = deepcopy(log)
    new_log._list.sort(key=sort_function, reverse=reverse)

    return new_log


def sort_lambda_stream(stream, sort_function, reverse=False):
    """
    Sort a stream based on a lambda expression

    Parameters
    ------------
    stream
        Stream
    sort_function
        Sort function
    reverse
        Boolean (sort by reverse order)

    Returns
    ------------
    stream
        Sorted stream
    """
    new_event_log = deepcopy(stream)
    new_event_log._list.sort(key=sort_function, reverse=reverse)

    return new_event_log


def sort_lambda(log, sort_function, reverse=False):
    """
    Sort a log based on lambda expression

    Parameters
    -------------
    log
        Log
    sort_function
        Sort function
    reverse
        Boolean (sort by reverse order)

    Returns
    -------------
    log
        Sorted log
    """
    if type(log) is EventLog:
        return sort_lambda_log(log, sort_function, reverse=reverse)
    return sort_lambda_stream(log, sort_function, reverse=reverse)

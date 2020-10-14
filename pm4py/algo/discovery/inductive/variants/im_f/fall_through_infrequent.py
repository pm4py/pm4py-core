from pm4py.objects.log import log
import logging

def empty_trace_filtering(l, f):
    enough_traces = False
    empty_traces_present, counter = __count_empty_traces(l)
    if counter >= len(l)*f:
        enough_traces = True

    if empty_traces_present:
        new_log = log.EventLog()
        for trace in l:
            if len(trace) != 0:
                new_log.append(trace)
        return empty_traces_present, enough_traces, new_log
    else:
        return False, False, l


def __count_empty_traces(l):
    counter = 0
    empty_traces_present = False
    for trace in l:
        if len(trace) == 0:
            empty_traces_present = True
            counter += 1

    return empty_traces_present, counter

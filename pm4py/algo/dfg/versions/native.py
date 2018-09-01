from collections import Counter
from pm4py.log import util


def apply(trace_log, parameters=None, activity_key=util.xes.DEFAULT_NAME_KEY, timestamp_key="time:timestamp"):
    '''
    Counts the number of directly follows occurrences, i.e. of the form <...a,b...>, in an event log.

    Parameters
    ----------
    trace_log
        Trace log
    parameters
        Possible parameters passed to the algorithms
    activity_key
        Field in the log that represents the activity (must be specified if different from concept:name)
    timestamp_key
        Field in the log that represents the timestamp

    Returns
    -------
    dfg
        DFG graph
    '''
    dfgs = map((lambda t: [(t[i - 1][activity_key], t[i][activity_key]) for i in range(1, len(t))]), trace_log)
    return Counter([dfg for list in dfgs for dfg in list])

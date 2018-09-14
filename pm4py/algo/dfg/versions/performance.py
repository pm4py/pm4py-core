from collections import Counter
from pm4py.log import util
from statistics import mean

def apply(trace_log, parameters=None, activity_key=util.xes.DEFAULT_NAME_KEY, timestamp_key="time:timestamp"):
    '''
    Measure performance between couples of attributes in the DFG graph

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

    dfgs0 = map((lambda t: [((t[i - 1][activity_key], t[i][activity_key]), (t[i][timestamp_key]-t[i-1][timestamp_key]).total_seconds())
                             for i in range(1, len(t))]), trace_log)
    ret0 = {}
    for el in dfgs0:
        for couple in el:
            if not couple[0] in ret0:
                ret0[couple[0]] = []
            ret0[couple[0]].append(couple[1])
    ret = Counter()
    for key in ret0:
        ret[key] = mean(ret0[key])
    return ret
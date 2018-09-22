from collections import Counter
from statistics import mean, median, stdev
from pm4py.util import constants
from pm4py.entities.log.util import xes

def apply(trace_log, parameters=None):
    '''
    Measure performance between couples of attributes in the DFG graph

    Parameters
    ----------
    trace_log
        Trace log
    parameters
        Possible parameters passed to the algorithms:
            aggregationMeasure -> performance aggregation measure (min, max, mean, median)
            activity_key -> Attribute to use as activity
            timestamp_key -> Attribute to use as timestamp

    Returns
    -------
    dfg
        DFG graph
    '''

    if parameters is None:
        parameters = {}

    activity_key = parameters[constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY
    timestamp_key = parameters[constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] if constants.PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else xes.DEFAULT_TIMESTAMP_KEY
    aggregationMeasure = parameters["aggregationMeasure"] if "aggregationMeasure" in parameters else "mean"

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
        if aggregationMeasure == "median":
            ret[key] = median(ret0[key])
        elif aggregationMeasure == "min":
            ret[key] = min(ret0[key])
        elif aggregationMeasure == "max":
            ret[key] = max(ret0[key])
        elif aggregationMeasure == "stdev":
            ret[key] = stdev(ret0[key])
        elif aggregationMeasure == "sum":
            ret[key] = sum(ret0[key])
        else:
            ret[key] = mean(ret0[key])

    return ret
from collections import Counter

from pm4py.objects.log.util.xes import DEFAULT_NAME_KEY
from pm4py.objects.log.util.xes import DEFAULT_TIMESTAMP_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_TIMESTAMP_KEY

# emergency fix to be refactored
try:
    from Lib.statistics import mean, median, stdev
except:
    from statistics import mean, median, stdev


def apply(log, parameters=None):
    """
    Measure performance between couples of attributes in the DFG graph

    Parameters
    ----------
    log
        Log
    parameters
        Possible parameters passed to the algorithms:
            aggregationMeasure -> performance aggregation measure (min, max, mean, median)
            activity_key -> Attribute to use as activity
            timestamp_key -> Attribute to use as timestamp

    Returns
    -------
    dfg
        DFG graph
    """

    if parameters is None:
        parameters = {}

    activity_key = parameters[
        PARAMETER_CONSTANT_ACTIVITY_KEY] if PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else DEFAULT_NAME_KEY
    timestamp_key = parameters[
        PARAMETER_CONSTANT_TIMESTAMP_KEY] if PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else DEFAULT_TIMESTAMP_KEY
    aggregation_measure = parameters["aggregationMeasure"] if "aggregationMeasure" in parameters else "mean"

    dfgs0 = map((lambda t: [
        ((t[i - 1][activity_key], t[i][activity_key]), (t[i][timestamp_key] - t[i - 1][timestamp_key]).total_seconds())
        for i in range(1, len(t))]), log)
    ret0 = {}
    for el in dfgs0:
        for couple in el:
            if not couple[0] in ret0:
                ret0[couple[0]] = []
            ret0[couple[0]].append(couple[1])
    ret = Counter()
    for key in ret0:
        if aggregation_measure == "median":
            ret[key] = median(ret0[key])
        elif aggregation_measure == "min":
            ret[key] = min(ret0[key])
        elif aggregation_measure == "max":
            ret[key] = max(ret0[key])
        elif aggregation_measure == "stdev":
            ret[key] = stdev(ret0[key])
        elif aggregation_measure == "sum":
            ret[key] = sum(ret0[key])
        else:
            ret[key] = mean(ret0[key])

    return ret

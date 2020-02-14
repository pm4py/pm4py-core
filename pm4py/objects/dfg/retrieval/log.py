from collections import Counter

from pm4py import util as pmutil
from pm4py.util import xes_constants as xes_util
from pm4py.util.xes_constants import DEFAULT_NAME_KEY
from pm4py.util.xes_constants import DEFAULT_TIMESTAMP_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_TIMESTAMP_KEY
from statistics import mean, median, stdev

WINDOW = "window"
DEFAULT_WINDOW = 1


def freq_triples(log, parameters=None):
    """
    Counts the number of directly follows occurrences, i.e. of the form <...a,b...>, in an event log.

    Parameters
    ----------
    log
        Trace log
    parameters
        Possible parameters passed to the algorithms:
            activity_key -> Attribute to use as activity

    Returns
    -------
    dfg
        DFG graph
    """
    if parameters is None:
        parameters = {}
    if pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY

    activity_key = parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]
    dfgs = map((lambda t: [(t[i - 2][activity_key], t[i - 1][activity_key], t[i][activity_key]) for i in range(2, len(t))]), log)
    return Counter([dfg for lista in dfgs for dfg in lista])


def native(log, parameters=None):
    """
    Counts the number of directly follows occurrences, i.e. of the form <...a,b...>, in an event log.

    Parameters
    ----------
    log
        Trace log
    parameters
        Possible parameters passed to the algorithms:
            activity_key -> Attribute to use as activity

    Returns
    -------
    dfg
        DFG graph
    """
    if parameters is None:
        parameters = {}
    if pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY

    window = parameters[WINDOW] if WINDOW in parameters else DEFAULT_WINDOW
    activity_key = parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]
    dfgs = map((lambda t: [(t[i - window][activity_key], t[i][activity_key]) for i in range(window, len(t))]), log)
    return Counter([dfg for lista in dfgs for dfg in lista])


def performance(log, parameters=None):
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

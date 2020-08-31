from collections import Counter

from pm4py.util import xes_constants as xes_util
from statistics import mean, median, stdev
from pm4py.util import constants, exec_utils
from enum import Enum


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    WINDOW = "window"
    AGGREGATION_MEASURE = "aggregationMeasure"
    KEEP_ONCE_PER_CASE = "keep_once_per_case"


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
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_util.DEFAULT_NAME_KEY)
    dfgs = map(
        (lambda t: [(t[i - 2][activity_key], t[i - 1][activity_key], t[i][activity_key]) for i in range(2, len(t))]),
        log)
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
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_util.DEFAULT_NAME_KEY)
    window = exec_utils.get_param_value(Parameters.WINDOW, parameters, 1)
    keep_once_per_case = exec_utils.get_param_value(Parameters.KEEP_ONCE_PER_CASE, parameters, False)
    if keep_once_per_case:
        dfgs = map((lambda t: set((t[i - window][activity_key], t[i][activity_key]) for i in range(window, len(t)))), log)
    else:
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

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_util.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes_util.DEFAULT_TIMESTAMP_KEY)
    aggregation_measure = exec_utils.get_param_value(Parameters.AGGREGATION_MEASURE, parameters, "mean")

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

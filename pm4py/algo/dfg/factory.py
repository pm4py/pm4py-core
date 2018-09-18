from pm4py.algo.dfg import versions as dfg_versions
from pm4py.log import util

DFG_NATIVE = 'native'
DFG_FREQUENCY = 'frequency'
DFG_PERFORMANCE = 'performance'

versions = {DFG_NATIVE: dfg_versions.native.apply, DFG_FREQUENCY: dfg_versions.native.apply, DFG_PERFORMANCE: dfg_versions.performance.apply}

def apply(trace_log, parameters=None, variant=DFG_NATIVE):
    """
    Calculates DFG graph (frequency or performance) starting from a trace log

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
    """
    return versions[variant](trace_log, parameters=parameters)
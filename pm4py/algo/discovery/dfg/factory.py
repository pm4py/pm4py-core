from pm4py.algo.discovery.dfg.versions import native, performance

DFG_NATIVE = 'native'
DFG_FREQUENCY = 'frequency'
DFG_PERFORMANCE = 'performance'
DFG_FREQUENCY_GREEDY = 'frequency_greedy'
DFG_PERFORMANCE_GREEDY = 'performance_greedy'

versions = {DFG_NATIVE: native.apply, DFG_FREQUENCY: native.apply, DFG_PERFORMANCE: performance.apply,
            DFG_FREQUENCY_GREEDY: native.apply, DFG_PERFORMANCE_GREEDY: performance.apply}


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
    variant
        Variant of the algorithm to use, possible values:
            native, frequency, performance, frequency_greedy, performance_greedy

    Returns
    -------
    dfg
        DFG graph
    """
    return versions[variant](trace_log, parameters=parameters)

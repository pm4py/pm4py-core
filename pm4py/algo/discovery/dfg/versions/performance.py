from pm4py.objects.dfg.retrieval import log as log_calc


def apply(log, parameters=None):
    """
    Measure performance between couples of attributes in the DFG graph

    Parameters
    ----------
    log
        Log
    parameters
        Possible parameters passed to the algorithms:
            Parameters.AGGREGATION_MEASURE -> performance aggregation measure (min, max, mean, median)
            Parameters.ACTIVITY_KEY -> Attribute to use as activity
            Parameters.TIMESTAMP_KEY -> Attribute to use as timestamp

    Returns
    -------
    dfg
        DFG graph
    """
    return log_calc.performance(log, parameters=parameters)

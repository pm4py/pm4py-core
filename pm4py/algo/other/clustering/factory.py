from pm4py.algo.other.clustering.versions import decisiontree

DECISIONTREE = "decisiontree"

VERSIONS = {DECISIONTREE: decisiontree.apply}


def apply(log, parameters=None, variant=DECISIONTREE):
    """
    Factory method to apply a log clustering algorithm

    Parameters
    -------------
    log
        Trace log object
    parameters
        Parameters of the algorithm
    variant
        Chosen clustering algorithm

    Returns
    -----------
    log_list
        A list containing, for each cluster, a different log
    """
    return VERSIONS[variant](log, parameters=parameters)

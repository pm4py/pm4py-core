from pm4py.algo.other.conceptdrift.versions import decisiontree

DECISIONTREE = "decisiontree"

VERSIONS = {DECISIONTREE: decisiontree.apply}


def apply(log, parameters=None, variant=DECISIONTREE):
    """
    Apply PCA + DBSCAN clustering, taking into account the control flow perspective but also the other perspectives,
    in order to possibly detect concept drift

    Parameters
    -------------
    log
        Log
    parameters
        Possible parameters of the algorithm
    variant
        Variant of the algorithm to apply, possible values: decisiontree
    """
    return VERSIONS[variant](log, parameters=parameters)

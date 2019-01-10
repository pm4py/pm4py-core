from pm4py.algo.sna.metrics.similar_activities.versions import classic

CLASSIC = "classic"

VERSIONS = {CLASSIC: classic.apply}


def apply(mco, parameters=None, variant=CLASSIC):
    """
    Calculate the Similar Activities metric

    Parameters
    ------------
    mco
        Matrix container object
    parameters
        Parameters of the algorithm
    variant
        Variant of the algorithm: classic
    """
    return VERSIONS[CLASSIC].apply(mco, parameters=parameters)

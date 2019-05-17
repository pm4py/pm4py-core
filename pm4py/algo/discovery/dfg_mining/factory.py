from pm4py.algo.discovery.dfg_mining.versions import classic

CLASSIC = "classic"

VERSIONS = {CLASSIC: classic.apply}


def apply(obj, variant=CLASSIC, parameters=None):
    """
    Applies the DFG mining on a given object (if it is a Pandas dataframe or a log, the DFG is calculated)

    Parameters
    -------------
    obj
        Object (DFG) (if it is a Pandas dataframe or a log, the DFG is calculated)
    variant
        Variant of the algorithm to apply. Possible values: classic
    parameters
        Parameters
    """
    return VERSIONS[variant](obj, parameters=parameters)

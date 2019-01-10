from pm4py.algo.sna.transformer.tracelog.versions import full, basic

FULL = "full"
BASIC = "basic"

VERSIONS = {FULL: full.apply, BASIC: basic.apply}


def apply(log, parameters=None, variant=FULL):
    """
    Create full matrix (containing resources and activities) from the trace log object

    Parameters
    ------------
    log
        Trace log
    parameters
        Parameters of the algorithm
    variant
        Variant of the algorithm to apply

    Returns
    ------------
    mco
        SNA Matrix container object
    """
    return VERSIONS[variant](log, parameters=parameters)

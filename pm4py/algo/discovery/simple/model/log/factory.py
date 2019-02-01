from pm4py.algo.discovery.simple.model.log.versions import classic

CLASSIC = "classic"

VERSIONS = {CLASSIC: classic.apply}


def apply(log, parameters=None, variant=CLASSIC, classic_output=False):
    """
    Gets a simple model out of a log

    Parameters
    -------------
    log
        Trace log
    parameters
        Parameters of the algorithm
    variant
        Variant of the algorithm to apply (choices: classic)
    classic_output
        Determine if the output shall contains directly the objects (e.g. net, initial_marking, final_marking)
        or can return a more detailed dictionary
    """
    return VERSIONS[variant](log, parameters=parameters, classic_output=classic_output)

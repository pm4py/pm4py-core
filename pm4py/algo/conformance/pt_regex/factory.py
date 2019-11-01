from pm4py.algo.conformance.pt_regex.versions import classic

CLASSIC = "classic"

VERSIONS = {CLASSIC: classic.apply}

def apply(log, process_tree, variant=CLASSIC, parameters=None):
    """
    Check the fitness of the log against the process tree

    NB: The conformance check is not yet working with trees containing an AND and/or an OR operator!

    Parameters
    ------------
    log
        Event log
    tree
        Process tree
    parameters
        Parameters of the algorithm, including the activity key

    Returns
    -------------
    list_fitness
        List of booleans values (True whether the case is fit, False otherwise)
    """
    return VERSIONS[variant](log, process_tree, parameters=parameters)

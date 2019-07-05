from pm4py.algo.discovery.causal.versions import alpha, heuristic

CAUSAL_ALPHA = 'alpha'
CAUSAL_HEURISTIC = 'heuristic'

versions = {CAUSAL_ALPHA: alpha.apply, CAUSAL_HEURISTIC: heuristic.apply}


def apply(dfg, variant=CAUSAL_ALPHA):
    """
    Computes the causal relation on the basis of a given directly follows graph.

    Parameters
    -----------
    dfg
        Directly follows graph
    variant
        Variant of the algorithm to use (classic)

    Returns
    -----------
    causal relations
        dict
    """
    return versions[variant](dfg)

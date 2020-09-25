from pm4py.algo.discovery.causal.versions import alpha, heuristic
import deprecation

CAUSAL_ALPHA = 'alpha'
CAUSAL_HEURISTIC = 'heuristic'

VERSIONS = {CAUSAL_ALPHA: alpha.apply, CAUSAL_HEURISTIC: heuristic.apply}

@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Use algorithm entrypoint instead (causal/factory)')
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
    return VERSIONS[variant](dfg)

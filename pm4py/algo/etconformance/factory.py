from pm4py.algo.etconformance.versions import token_based

TOKEN_BASED = "token_based"
VERSIONS = {TOKEN_BASED: token_based.apply}

def apply(log, net, marking, final_marking, activity_key="concept:name", variant="token_based"):
    """
    Factory method to apply ET Conformance

    Parameters
    -----------
    log
        Trace log
    net
        Petri net
    marking
        Initial marking
    final_marking
        Final marking
    activity_key
        Activity key (must be specified if different from token based)
    variant
        Variant of the algorithm that should be applied
    """
    return VERSIONS[variant](log, net, marking, final_marking, activity_key=activity_key)
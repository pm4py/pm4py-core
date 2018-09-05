from pm4py.evaluation.precision.versions import etconformance_token

ETCONFORMANCE_TOKEN = "etconformance"
VERSIONS = {ETCONFORMANCE_TOKEN: etconformance_token.apply}

def apply(log, net, marking, final_marking, activity_key="concept:name", variant="etconformance"):
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
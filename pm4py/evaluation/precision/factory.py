from pm4py.evaluation.precision.versions import etconformance_token

ETCONFORMANCE_TOKEN = "etconformance"
VERSIONS = {ETCONFORMANCE_TOKEN: etconformance_token.apply}


def apply(log, net, marking, final_marking, parameters=None, variant="etconformance"):
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
    parameters
        Parameters of the algorithm, including:
            pm4py.util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY -> Activity key
    variant
        Variant of the algorithm that should be applied
    """
    return VERSIONS[variant](log, net, marking, final_marking, parameters=parameters)

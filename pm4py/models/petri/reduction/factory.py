from pm4py.models.petri.reduction.versions import tokenbased

TOKENBASED = "tokenbased"

VERSIONS = {TOKENBASED: tokenbased.apply}

def apply(net, parameters=None, variant="tokenbased"):
    """
    Apply a reduction technique specified in variant

    Parameters
    -----------
    net
        Petri net
    parameters
        Parameters of the algorithm, depending on the variant, possibly including:
            aligned_traces -> Result of alignment according to token-based replay

    Returns
    -----------
    net
        Reduced Petri net
    """
    return VERSIONS[variant](net, parameters=parameters)
from pm4py.objects.conversion.tree_to_petri.versions import classic

CLASSIC = "classic"

VERSIONS = {CLASSIC: classic.apply}


def apply(tree, parameters=None, variant="classic"):
    """
    Factory method for converting from Process Tree to Petri net

    Parameters
    -----------
    tree
        Process tree
    parameters
        Parameters of the algorithm
    variant
        Chosen variant of the algorithm (only classic)

    Returns
    -----------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    return VERSIONS[variant](tree, parameters=parameters)

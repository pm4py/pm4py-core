from pm4py.objects.conversion.process_tree.versions import to_petri_net

TO_PETRI_NET = "to_petri_net"

VERSIONS = {TO_PETRI_NET: to_petri_net.apply}


def apply(tree, parameters=None, variant=TO_PETRI_NET):
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

from pm4py.objects.conversion.process_tree.versions import to_petri_net
from pm4py.objects.conversion.process_tree.versions import to_petri_net_transition_bordered
from pm4py.util import exec_utils
from enum import Enum


class Variants(Enum):
    TO_PETRI_NET = to_petri_net
    TO_PETRI_NET_TRANSITION_BORDERED = to_petri_net_transition_bordered


def apply(tree, parameters=None, variant=Variants.TO_PETRI_NET):
    """
    Method for converting from Process Tree to Petri net

    Parameters
    -----------
    tree
        Process tree
    parameters
        Parameters of the algorithm
    variant
        Chosen variant of the algorithm:
            - Variants.TO_PETRI_NET
            - Variants.TO_PETRI_NET_TRANSITION_BORDERED

    Returns
    -----------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    return exec_utils.get_variant(variant).apply(tree, parameters=parameters)

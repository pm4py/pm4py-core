from pm4py.objects.conversion.process_tree.versions import to_petri_net
from pm4py.objects.conversion.process_tree.versions import to_petri_net_transition_bordered
import deprecation

TO_PETRI_NET = "to_petri_net" # old / legacy code
TO_PETRI_NET_TRANSITION_BORDERED = "to_petri_net_transition_bordered"

VERSIONS = {TO_PETRI_NET: to_petri_net.apply, TO_PETRI_NET_TRANSITION_BORDERED: to_petri_net_transition_bordered.apply}


@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Use algorithm entrypoint instead (conversion/process_tree/factory)')
def apply(tree, parameters=None, variant=TO_PETRI_NET):
    """
    Method for converting from Process Tree to Petri net

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

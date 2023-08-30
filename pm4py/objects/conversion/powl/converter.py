from pm4py.objects.conversion.powl.variants import to_petri_net
from pm4py.util import exec_utils
from enum import Enum


class Variants(Enum):
    TO_PETRI_NET = to_petri_net

def apply(powl, parameters=None, variant=Variants.TO_PETRI_NET):
    """
    Method for converting from POWL to Petri net

    Parameters
    -----------
    powl
        POWL model
    parameters
        Parameters of the algorithm
    variant
        Chosen variant of the algorithm:
            - Variants.TO_PETRI_NET

    Returns
    -----------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    return exec_utils.get_variant(variant).apply(powl, parameters=parameters)

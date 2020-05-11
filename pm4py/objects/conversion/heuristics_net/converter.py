from pm4py.objects.conversion.heuristics_net.versions import to_petri_net
from enum import Enum
from pm4py.util import exec_utils


class Variants(Enum):
    TO_PETRI_NET = to_petri_net


def apply(heu_net, parameters=None, variant=Variants.TO_PETRI_NET):
    """
    Converts an Heuristics Net to a different type of object

    Parameters
    --------------
    heu_net
        Heuristics net
    parameters
        Possible parameters of the algorithm
    variant
        Variant of the algorithm:
            - Variants.TO_PETRI_NET
    """
    return exec_utils.get_variant(variant).apply(heu_net, parameters=parameters)

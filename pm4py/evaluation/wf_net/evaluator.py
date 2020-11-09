from enum import Enum

from pm4py.evaluation.wf_net.variants import petri_net
from pm4py.util import exec_utils


class Variants(Enum):
    PETRI_NET = petri_net


def apply(net, parameters=None, variant=Variants.PETRI_NET):
    """
    Checks if a Petri net is a workflow net

    Parameters
    ---------------
    net
        Petri net
    parameters
        Parameters of the algorithm
    variant
        Variant of the algorithm, possibe values:
        - Variants.PETRI_NET

    Returns
    ---------------
    boolean
        Boolean value
    """
    return exec_utils.get_variant(variant).apply(net, parameters=parameters)

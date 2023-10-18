from enum import Enum

from pm4py.algo.analysis.workflow_net.variants import petri_net
from pm4py.util import exec_utils
from typing import Optional, Dict, Any
from pm4py.objects.petri_net.obj import PetriNet


class Variants(Enum):
    PETRI_NET = petri_net


def apply(net: PetriNet, parameters: Optional[Dict[Any, Any]] = None, variant=Variants.PETRI_NET) -> bool:
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

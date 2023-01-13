from pm4py.objects.petri_net.obj import PetriNet
from typing import Optional, Dict, Any


def apply(petri_net: PetriNet, parameters: Optional[Dict[Any, Any]] = None) -> float:
    """
    Computes the extended Cardoso metric as described in the paper:

    "Complexity Metrics for Workflow Nets"
    Lassen, Kristian Bisgaard, and Wil MP van der Aalst

    Parameters
    -------------
    petri_net
        Petri net

    Returns
    -------------
    ext_cardoso_metric
        Extended Cardoso metric
    """
    if parameters is None:
        parameters = {}

    ext_card = 0

    for place in petri_net.places:
        targets = set()
        for out_arc in place.out_arcs:
            for out_arc2 in out_arc.target.out_arcs:
                targets.add(out_arc2.target)
        ext_card += len(targets)

    return ext_card

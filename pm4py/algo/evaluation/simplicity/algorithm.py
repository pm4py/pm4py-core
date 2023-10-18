from pm4py.algo.evaluation.simplicity.variants import arc_degree, extended_cardoso, extended_cyclomatic
from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any
from pm4py.objects.petri_net.obj import PetriNet


class Variants(Enum):
    SIMPLICITY_ARC_DEGREE = arc_degree
    EXTENDED_CARDOSO = extended_cardoso
    EXTENDED_CYCLOMATIC = extended_cyclomatic


SIMPLICITY_ARC_DEGREE = Variants.SIMPLICITY_ARC_DEGREE
EXTENDED_CARDOSO = Variants.EXTENDED_CARDOSO
EXTENDED_CYCLOMATIC = Variants.EXTENDED_CYCLOMATIC

VERSIONS = {SIMPLICITY_ARC_DEGREE, EXTENDED_CARDOSO, EXTENDED_CYCLOMATIC}


def apply(petri_net: PetriNet, parameters: Optional[Dict[Any, Any]] = None, variant=SIMPLICITY_ARC_DEGREE) -> float:
    return exec_utils.get_variant(variant).apply(petri_net, parameters=parameters)

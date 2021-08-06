from pm4py.algo.evaluation.simplicity.variants import arc_degree
from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any, Union, Tuple
from pm4py.objects.log.obj import EventLog, EventStream
from pm4py.objects.petri_net.obj import PetriNet, Marking
import pandas as pd


class Variants(Enum):
    SIMPLICITY_ARC_DEGREE = arc_degree


SIMPLICITY_ARC_DEGREE = Variants.SIMPLICITY_ARC_DEGREE

VERSIONS = {SIMPLICITY_ARC_DEGREE}


def apply(petri_net: PetriNet, parameters: Optional[Dict[Any, Any]] = None, variant=SIMPLICITY_ARC_DEGREE) -> float:
    return exec_utils.get_variant(variant).apply(petri_net, parameters=parameters)

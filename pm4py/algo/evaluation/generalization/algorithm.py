from pm4py.algo.evaluation.generalization.variants import token_based
from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any, Union, Tuple
from pm4py.objects.log.obj import EventLog, EventStream
from pm4py.objects.petri_net.obj import PetriNet, Marking
import pandas as pd


class Variants(Enum):
    GENERALIZATION_TOKEN = token_based


GENERALIZATION_TOKEN = Variants.GENERALIZATION_TOKEN
VERSIONS = {GENERALIZATION_TOKEN}


def apply(log: Union[EventLog, EventStream, pd.DataFrame], petri_net: PetriNet, initial_marking: Marking, final_marking: Marking, parameters: Optional[Dict[Any, Any]] = None, variant=GENERALIZATION_TOKEN) -> float:
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(log,
                                                 petri_net,
                                                 initial_marking, final_marking, parameters=parameters)

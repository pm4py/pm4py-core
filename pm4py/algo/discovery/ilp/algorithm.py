from enum import Enum
from pm4py.util import exec_utils
from pm4py.algo.discovery.ilp.variants import classic
from typing import Union, Optional, Dict, Any, Tuple
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd


class Variants(Enum):
    CLASSIC = classic


def apply(log: Union[EventLog, EventStream, pd.DataFrame], variant = Variants.CLASSIC, parameters: Optional[Dict[Any, Any]] = None) -> Tuple[PetriNet, Marking, Marking]:
    """
    Discovers a Petri net using the ILP miner.

    Parameters
    ---------------
    log
        Event log / Event stream / Pandas dataframe
    variant
        Variant of the algorithm to be used, possible values:
        - Variants.CLASSIC
    parameters
        Variant-specific parameters

    Returns
    ---------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    """
    return exec_utils.get_variant(variant).apply(log, parameters)

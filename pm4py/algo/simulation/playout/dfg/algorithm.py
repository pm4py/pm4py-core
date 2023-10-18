from pm4py.algo.simulation.playout.dfg.variants import classic, performance
from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any, Union, Tuple
from pm4py.objects.log.obj import EventLog


class Variants(Enum):
    CLASSIC = classic
    PERFORMANCE = performance


def apply(dfg: Dict[Tuple[str, str], int], start_activities: Dict[str, int], end_activities: Dict[str, int], variant=Variants.CLASSIC, parameters: Optional[Dict[Any, Any]] = None) -> Union[EventLog, Dict[Tuple[str, str], int]]:
    """
    Applies the playout algorithm on a DFG, extracting the most likely traces according to the DFG

    Parameters
    ---------------
    dfg
        *Complete* DFG
    start_activities
        Start activities
    end_activities
        End activities
    variant
        Variant of the playout to be used, possible values:
        - Variants.CLASSIC
        - Variants.PERFORMANCE
    parameters
        Parameters of the algorithm

    Returns
    ---------------
    simulated_log
        Simulated log
    """
    return exec_utils.get_variant(variant).apply(dfg, start_activities, end_activities, parameters=parameters)

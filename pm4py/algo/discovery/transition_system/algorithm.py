from pm4py.algo.discovery.transition_system.variants import view_based
from pm4py.util import exec_utils
from enum import Enum
from pm4py.objects.transition_system.obj import TransitionSystem
from typing import Optional, Dict, Any, Union, Tuple
from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd


class Variants(Enum):
    VIEW_BASED = view_based

VERSIONS = {Variants.VIEW_BASED}
VIEW_BASED = Variants.VIEW_BASED
DEFAULT_VARIANT = Variants.VIEW_BASED


def apply(log: Union[EventLog, EventStream, pd.DataFrame], parameters: Optional[Dict[Any, Any]] = None, variant=DEFAULT_VARIANT) -> TransitionSystem:
    """
    Find transition system given log

    Parameters
    -----------
    log
        Log
    parameters
        Possible parameters of the algorithm, including:
            Parameters.PARAM_KEY_VIEW
            Parameters.PARAM_KEY_WINDOW
            Parameters.PARAM_KEY_DIRECTION
    variant
        Variant of the algorithm to use, including:
            Variants.VIEW_BASED

    Returns
    ----------
    ts
        Transition system
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(log, parameters=parameters)

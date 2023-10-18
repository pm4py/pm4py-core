from pm4py.util import exec_utils
from enum import Enum
from pm4py.algo.discovery.declare.variants import classic
from pm4py.objects.log.obj import EventLog
import pandas as pd
from typing import Union, Dict, Optional, Any


class Variants(Enum):
    CLASSIC = classic


def apply(log: Union[EventLog, pd.DataFrame], variant=Variants.CLASSIC, parameters: Optional[Dict[Any, Any]] = None) -> Dict[str, Dict[Any, Dict[str, int]]]:
    """
    Discovers a DECLARE model from the provided event log

    Parameters
    ---------------
    log
        Log object (EventLog, Pandas dataframe)
    variant
        Variant of the algorithm to be used, including:
        - Variants.CLASSIC
    parameters
        Variant-specific parameters

    Returns
    ---------------
    declare_model
        DECLARE model (as Python dictionary), where each template is associated with its own rules
    """
    return exec_utils.get_variant(variant).apply(log, parameters)

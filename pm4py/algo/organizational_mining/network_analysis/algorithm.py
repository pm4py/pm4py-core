from pm4py.algo.organizational_mining.network_analysis.variants import dataframe
from enum import Enum
from pm4py.util import exec_utils
from typing import Dict, Optional, Any, Tuple, Union
import pandas as pd
from pm4py.objects.log.obj import EventLog, EventStream
from pm4py.objects.conversion.log import converter as log_converter


class Variants(Enum):
    DATAFRAME = dataframe


def apply(log: Union[pd.DataFrame, EventLog, EventStream], variant=Variants.DATAFRAME, parameters: Optional[Dict[Any, Any]] = None) -> Dict[Tuple[str, str], Dict[str, Any]]:
    """
    Performs the network analysis on the provided event log

    Parameters
    ----------------
    log
        Event log
    parameters
        Version-specific parameters

    Returns
    ----------------
    network_analysis
        Edges of the network analysis (first key: edge; second key: type; value: number of occurrences)
    """
    return exec_utils.get_variant(variant).apply(log_converter.apply(log, variant=log_converter.Variants.TO_DATA_FRAME, parameters=parameters), parameters=parameters)

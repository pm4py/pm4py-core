from pm4py.algo.discovery.ocel.link_analysis.variants import classic
from enum import Enum
from pm4py.util import exec_utils
import pandas as pd
from typing import Optional, Dict, Any
from pm4py.objects.log.obj import EventLog, EventStream
from typing import Union
from pm4py.objects.conversion.log import converter


class Variants(Enum):
    CLASSIC = classic


def apply(log: Union[EventLog, EventStream, pd.DataFrame], variant=Variants.CLASSIC, parameters: Optional[Dict[Any, Any]] = None) -> pd.DataFrame:
    """
    Applies a link analysis algorithm on the provided log object.

    Parameters
    -----------------
    log
        Event log
    variant
        Variant of the algorithm to consider
    parameters
        Variant-specific parameters

    Returns
    -----------------
    link_analysis_dataframe
        Link analysis dataframe
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(converter.apply(log, variant=converter.Variants.TO_DATA_FRAME, parameters=parameters), parameters=parameters)

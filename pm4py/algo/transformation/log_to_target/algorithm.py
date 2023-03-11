from enum import Enum
from pm4py.algo.transformation.log_to_target.variants import next_activity, next_time, remaining_time
from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd
from typing import Union, Dict, Optional, Any, Tuple, List
from pm4py.util import exec_utils


class Variants(Enum):
    NEXT_ACTIVITY = next_activity
    NEXT_TIME = next_time
    REMAINING_TIME = remaining_time


def apply(log: Union[EventLog, EventStream, pd.DataFrame], variant=None, parameters: Optional[Dict[Any, Any]] = None) -> Tuple[Any, List[str]]:
    """
    Extracts from the event log
    the target vector for a specific ML use case

    Parameters
    ---------------
    log
        Event log / Event stream / Pandas dataframe
    variant
        Specification of the target vector:
        - Variants.NEXT_ACTIVITY => encodes the next activity
        - Variants.NEXT_TIME => encodes the next timestamp
        - Variants.REMAINING_TIME => encodes the remaining time

    Returns
    --------------
    vector
        Target vector for the specified ML use case
    classes
        Classes (for every column of the target vector)
    """
    if variant is None:
        raise Exception("please provide the variant between: Variants.NEXT_ACTIVITY, Variants.NEXT_TIME, Variants.REMAINING_TIME")
    return exec_utils.get_variant(variant).apply(log, parameters=parameters)

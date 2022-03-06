from enum import Enum
from typing import Optional, Dict, Any, Union

from pm4py.algo.conformance.alignments.edit_distance.variants import edit_distance
from pm4py.objects.log.obj import EventLog
from pm4py.util import exec_utils
from pm4py.util import typing
import pandas as pd


class Variants(Enum):
    EDIT_DISTANCE = edit_distance


def apply(log1: Union[EventLog, pd.DataFrame], log2: Union[EventLog, pd.DataFrame], variant=Variants.EDIT_DISTANCE,
          parameters: Optional[Dict[Any, Any]] = None) -> typing.ListAlignments:
    """
    Aligns each trace of the first log against the second log

    Parameters
    --------------
    log1
        First log
    log2
        Second log
    variant
        Variant of the algorithm, possible values:
        - Variants.EDIT_DISTANCE: minimizes the edit distance
    parameters
        Parameters of the algorithm

    Returns
    ---------------
    aligned_traces
        List that contains, for each trace of the first log, the corresponding alignment
    """
    return exec_utils.get_variant(variant).apply(log1, log2, parameters=parameters)

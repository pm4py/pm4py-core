from pm4py.algo.discovery.ocel.interleavings.variants import timestamp_interleavings
from enum import Enum
from pm4py.util import exec_utils
import pandas as pd
from typing import Optional, Dict, Any


class Variants(Enum):
    TIMESTAMP_INTERLEAVINGS = timestamp_interleavings


def apply(left_df: pd.DataFrame, right_df: pd.DataFrame, case_relations: pd.DataFrame, variant=Variants.TIMESTAMP_INTERLEAVINGS, parameters: Optional[Dict[Any, Any]] = None):
    """
    Discover the interleavings between two dataframes, given also a dataframe about the relations of the cases.

    Parameters
    -----------------
    left_df
        Left dataframe
    right_df
        Right dataframe
    case_relations
        Dictionary associating the cases of the first dataframe (column: case:concept:name_LEFT) to the
        cases of the second dataframe (column: case:concept:name_RIGHT)
    variant
        Variant of the algorithm to be used, possible values:
        - Variants.TIMESTAMP_INTERLEAVINGS
    parameters
        Variant-specific parameters

    Returns
    -----------------
    interleavings
        Interleavings dataframe
    """
    return exec_utils.get_variant(variant).apply(left_df, right_df, case_relations, parameters)

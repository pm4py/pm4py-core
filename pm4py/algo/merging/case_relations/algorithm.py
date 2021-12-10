from pm4py.algo.merging.case_relations.variants import pandas
from enum import Enum
import pandas as pd
from typing import Optional, Dict, Any
from pm4py.util import exec_utils


class Variants(Enum):
    PANDAS = pandas


def apply(dataframe1: pd.DataFrame, dataframe2: pd.DataFrame, case_relations: pd.DataFrame, variant=Variants.PANDAS,
          parameters: Optional[Dict[Any, Any]] = None) -> pd.DataFrame:
    """
    Merges the two dataframes (dataframe1 and dataframe2), inserting the events of the second
    dataframe inside the cases of the first dataframe.
    This is done using a background knowledge provided in the case_relations dataframe, where the cases of the two dataframes
    are put in relations.
    E.g., if in dataframe1 and dataframe2 there are two case ID columns (case:concept:name),
    they are put in relations by case_relations having two columns case:concept:name_LEFT and case:concept:name_RIGHT

    Parameters
    -----------------
    dataframe1
        Reference dataframe (in which the events of the other dataframe are inserted)
    dataframe2
        Second dataframe (to insert in the cases of the first)
    case_relations
        Case relations dataframe
    variant
        Variant of the algorithm to use, available ones:
            - Variants.PANDAS
    parameters
        Variant-specific parameters

    Returns
    ----------------
    merged_dataframe
        Merged dataframe
    """
    return exec_utils.get_variant(variant).apply(dataframe1, dataframe2, case_relations, parameters=parameters)

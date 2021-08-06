from pm4py.statistics.traces.generic.pandas import case_statistics
from enum import Enum
from typing import Optional, Dict, Any, Union, Tuple, List, Set
from pm4py.objects.log.obj import EventLog, Trace
import pandas as pd


def get_variants_count(df: pd.DataFrame, parameters: Optional[Dict[Any, Any]] = None) -> Union[Dict[str, int], Dict[List[str], int]]:
    """
    Gets the dictionary of variants from the current dataframe

    Parameters
    --------------
    df
        Dataframe
    parameters
        Possible parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> Column that contains the activity

    Returns
    --------------
    variants_set
        Dictionary of variants in the log
    """
    if parameters is None:
        parameters = {}
    var_stats = case_statistics.get_variant_statistics(df, parameters=parameters)
    if var_stats:
        count_key = list(x for x in var_stats[0].keys() if not x == "variant")[0]
        return {x["variant"]: x[count_key] for x in var_stats}
    return {}


def get_variants_set(df: pd.DataFrame, parameters: Optional[Dict[Any, Any]] = None) -> Union[Set[str], Set[List[str]]]:
    """
    Gets the set of variants from the current dataframe

    Parameters
    --------------
    df
        Dataframe
    parameters
        Possible parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> Column that contains the activity

    Returns
    --------------
    variants_set
        Set of variants in the log
    """
    if parameters is None:
        parameters = {}
    var_stats = case_statistics.get_variant_statistics(df, parameters=parameters)
    return set(x["variant"] for x in var_stats)

from typing import Optional, Dict, Any, Union, List, Set

import pandas as pd

from pm4py.objects.log.util import pandas_numpy_variants


def get_variants_count(df: pd.DataFrame, parameters: Optional[Dict[Any, Any]] = None) -> Union[
    Dict[str, int], Dict[List[str], int]]:
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

    variants_counter, case_variant = pandas_numpy_variants.apply(df, parameters=parameters)

    return variants_counter


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

    variants_dict = get_variants_count(df, parameters=parameters)

    return set(variants_dict.keys())

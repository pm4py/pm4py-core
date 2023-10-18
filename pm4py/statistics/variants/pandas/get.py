'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
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

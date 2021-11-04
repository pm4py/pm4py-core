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
import pandas as pd

from pm4py.util.constants import CASE_CONCEPT_NAME
from pm4py.util.xes_constants import DEFAULT_NAME_KEY
from pm4py.util.xes_constants import DEFAULT_TIMESTAMP_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ATTRIBUTE_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_CASEID_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_TIMESTAMP_KEY
from pm4py.util.constants import DEFAULT_VARIANT_SEP
from enum import Enum
from pm4py.util import exec_utils
from copy import copy
import deprecation
from typing import Optional, Dict, Any, Union, Tuple, List
import pandas as pd
import sys


class Parameters(Enum):
    CASE_ID_KEY = PARAMETER_CONSTANT_CASEID_KEY
    ATTRIBUTE_KEY = PARAMETER_CONSTANT_ATTRIBUTE_KEY
    TIMESTAMP_KEY = PARAMETER_CONSTANT_TIMESTAMP_KEY
    DECREASING_FACTOR = "decreasingFactor"
    POSITIVE = "positive"
    MIN_PERFORMANCE = "min_performance"
    MAX_PERFORMANCE = "max_performance"


def apply(df: pd.DataFrame, paths: List[Tuple[str, str]], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> pd.DataFrame:
    """
    Apply a filter on traces containing / not containing a path

    Parameters
    ----------
    df
        Dataframe
    paths
        Paths to filter on
    parameters
        Possible parameters of the algorithm, including:
            Parameters.CASE_ID_KEY -> Case ID column in the dataframe
            Parameters.ATTRIBUTE_KEY -> Attribute we want to filter
            Parameters.POSITIVE -> Specifies if the filter should be applied including traces (positive=True)
            or excluding traces (positive=False)
    Returns
    ----------
    df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}
    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME)
    attribute_key = exec_utils.get_param_value(Parameters.ATTRIBUTE_KEY, parameters, DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)
    paths = [path[0] + DEFAULT_VARIANT_SEP + path[1] for path in paths]
    df = df.sort_values([case_id_glue, timestamp_key])
    filt_df = df[[case_id_glue, attribute_key]]
    filt_dif_shifted = filt_df.shift(-1)
    filt_dif_shifted.columns = [str(col) + '_2' for col in filt_dif_shifted.columns]
    stacked_df = pd.concat([filt_df, filt_dif_shifted], axis=1)
    stacked_df = stacked_df[stacked_df[case_id_glue] == stacked_df[case_id_glue + '_2']]
    stacked_df["@@path"] = stacked_df[attribute_key] + DEFAULT_VARIANT_SEP + stacked_df[attribute_key + "_2"]
    stacked_df = stacked_df[stacked_df["@@path"].isin(paths)]
    i1 = df.set_index(case_id_glue).index
    i2 = stacked_df.set_index(case_id_glue).index
    if positive:
        ret = df[i1.isin(i2)]
    else:
        ret = df[~i1.isin(i2)]

    ret.attrs = copy(df.attrs) if hasattr(df, 'attrs') else {}
    return ret


def apply_performance(df: pd.DataFrame, provided_path: Tuple[str, str], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> pd.DataFrame:
    """
    Filters the cases of a dataframe where there is at least one occurrence of the provided path
    occurring in the defined timedelta range.

    Parameters
    ----------
    df
        Dataframe
    paths
        Paths to filter on
    parameters
        Possible parameters of the algorithm, including:
            Parameters.CASE_ID_KEY -> Case ID column in the dataframe
            Parameters.ATTRIBUTE_KEY -> Attribute we want to filter
            Parameters.TIMESTAMP_KEY -> Attribute identifying the timestamp in the log
            Parameters.POSITIVE -> Specifies if the filter should be applied including traces (positive=True)
            or excluding traces (positive=False)
            Parameters.MIN_PERFORMANCE -> Minimal allowed performance of the provided path
            Parameters.MAX_PERFORMANCE -> Maximal allowed performance of the provided path

    Returns
    ----------
    df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}
    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME)
    attribute_key = exec_utils.get_param_value(Parameters.ATTRIBUTE_KEY, parameters, DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)
    provided_path = provided_path[0] + DEFAULT_VARIANT_SEP + provided_path[1]
    min_performance = exec_utils.get_param_value(Parameters.MIN_PERFORMANCE, parameters, 0)
    max_performance = exec_utils.get_param_value(Parameters.MAX_PERFORMANCE, parameters, sys.maxsize)
    df = df.sort_values([case_id_glue, timestamp_key])
    filt_df = df[[case_id_glue, attribute_key, timestamp_key]]
    filt_dif_shifted = filt_df.shift(-1)
    filt_dif_shifted.columns = [str(col) + '_2' for col in filt_dif_shifted.columns]
    stacked_df = pd.concat([filt_df, filt_dif_shifted], axis=1)
    stacked_df["@@path"] = stacked_df[attribute_key] + DEFAULT_VARIANT_SEP + stacked_df[attribute_key + "_2"]
    stacked_df = stacked_df[stacked_df["@@path"] == provided_path]
    stacked_df["@@timedelta"] = (stacked_df[timestamp_key + "_2"] - stacked_df[timestamp_key]).astype('timedelta64[s]')
    stacked_df = stacked_df[stacked_df["@@timedelta"] >= min_performance]
    stacked_df = stacked_df[stacked_df["@@timedelta"] <= max_performance]
    i1 = df.set_index(case_id_glue).index
    i2 = stacked_df.set_index(case_id_glue).index
    if positive:
        ret = df[i1.isin(i2)]
    else:
        ret = df[~i1.isin(i2)]

    ret.attrs = copy(df.attrs) if hasattr(df, 'attrs') else {}
    return ret


@deprecation.deprecated("2.2.11", "3.0.0", details="Removed")
def apply_auto_filter(df, parameters=None):
    del df
    del parameters
    raise Exception("apply_auto_filter method not available for paths filter on dataframe")

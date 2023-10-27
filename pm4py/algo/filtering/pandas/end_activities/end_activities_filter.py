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
from pm4py.statistics.end_activities.pandas.get import get_end_activities
from pm4py.util.constants import CASE_CONCEPT_NAME
from pm4py.util import xes_constants as xes
from pm4py.util.xes_constants import DEFAULT_NAME_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_CASEID_KEY, PARAMETER_CONSTANT_ACTIVITY_KEY, GROUPED_DATAFRAME, \
    RETURN_EA_COUNT_DICT_AUTOFILTER
from enum import Enum
from pm4py.util import exec_utils
from copy import copy
from typing import Optional, Dict, Any, Union, List
import pandas as pd


class Parameters(Enum):
    CASE_ID_KEY = PARAMETER_CONSTANT_CASEID_KEY
    ACTIVITY_KEY = PARAMETER_CONSTANT_ACTIVITY_KEY
    DECREASING_FACTOR = "decreasingFactor"
    GROUP_DATAFRAME = GROUPED_DATAFRAME
    POSITIVE = "positive"
    RETURN_EA_COUNT = RETURN_EA_COUNT_DICT_AUTOFILTER


def apply(df: pd.DataFrame, values: List[str], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> pd.DataFrame:
    """
    Filter dataframe on end activities

    Parameters
    ----------
    df
        Dataframe
    values
        Values to filter on
    parameters
        Possible parameters of the algorithm, including:
            Parameters.CASE_ID_KEY -> Case ID column in the dataframe
            Parameters.ACTIVITY_KEY -> Column that represents the activity
            Parameters.POSITIVE -> Specifies if the filtered should be applied including traces (positive=True)
            or excluding traces (positive=False)

    Returns
    ----------
    df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, DEFAULT_NAME_KEY)
    grouped_df = exec_utils.get_param_value(Parameters.GROUP_DATAFRAME, parameters, None)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)

    return filter_df_on_end_activities(df, values, case_id_glue=case_id_glue, activity_key=activity_key,
                                       positive=positive, grouped_df=grouped_df)


def filter_df_on_end_activities(df, values, case_id_glue=CASE_CONCEPT_NAME,
                                activity_key=xes.DEFAULT_NAME_KEY, grouped_df=None, positive=True):
    """
    Filter dataframe on end activities

    Parameters
    ----------
    df
        Dataframe
    values
        Values to filter on
    case_id_glue
        Case ID column in the dataframe
    activity_key
        Column that represent the activity
    positive
        Specifies if the filtered should be applied including traces (positive=True) or excluding traces
        (positive=False)

    Returns
    ----------
    df
        Filtered dataframe
    """
    if grouped_df is None:
        grouped_df = df.groupby(case_id_glue, sort=False)
    gdf = grouped_df[activity_key].last().isin(values)
    i1 = df.set_index(case_id_glue).index
    i2 = gdf[gdf].index
    if positive:
        ret = df[i1.isin(i2)]
    else:
        ret = df[~i1.isin(i2)]
    ret.attrs = copy(df.attrs) if hasattr(df, 'attrs') else {}
    return ret


def filter_df_on_end_activities_nocc(df, nocc, ea_count0=None, case_id_glue=CASE_CONCEPT_NAME,
                                     grouped_df=None,
                                     activity_key=xes.DEFAULT_NAME_KEY, return_dict=False, most_common_variant=None):
    """
    Filter dataframe on end activities number of occurrences

    Parameters
    -----------
    df
        Dataframe
    nocc
        Minimum number of occurrences of the end activity
    ea_count0
        (if provided) Dictionary that associates each end activity with its count
    case_id_glue
        Column that contains the Case ID
    activity_key
        Column that contains the activity
    grouped_df
        Grouped dataframe
    return_dict
        Return dict
    """
    if most_common_variant is None:
        most_common_variant = []

    if len(df) > 0:
        if grouped_df is None:
            grouped_df = df.groupby(case_id_glue, sort=False)
        first_eve_df = grouped_df.last()
        if ea_count0 is None:
            parameters = {
                Parameters.CASE_ID_KEY: case_id_glue,
                Parameters.ACTIVITY_KEY: activity_key,
                Parameters.GROUP_DATAFRAME: grouped_df
            }
            ea_count0 = get_end_activities(df, parameters=parameters)
        ea_count = [k for k, v in ea_count0.items() if
                    v >= nocc or (len(most_common_variant) > 0 and k == most_common_variant[-1])]
        ea_count_dict = {k: v for k, v in ea_count0.items() if
                         v >= nocc or (len(most_common_variant) > 0 and k == most_common_variant[-1])}
        if len(ea_count) < len(ea_count0):
            first_eve_df = first_eve_df[first_eve_df[activity_key].isin(ea_count)]
            i1 = df.set_index(case_id_glue).index
            i2 = first_eve_df.index
            ret = df[i1.isin(i2)]
            ret.attrs = copy(df.attrs) if hasattr(df, 'attrs') else {}
            if return_dict:
                return ret, ea_count_dict
            return ret
        if return_dict:
            return df, ea_count_dict
    return df

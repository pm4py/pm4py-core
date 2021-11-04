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
from pm4py.algo.filtering.common import filtering_constants
from pm4py.algo.filtering.common.end_activities import end_activities_common
from pm4py.statistics.end_activities.pandas.get import get_end_activities
from pm4py.util.constants import CASE_CONCEPT_NAME
from pm4py.util import xes_constants as xes
from pm4py.util.xes_constants import DEFAULT_NAME_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_CASEID_KEY, PARAMETER_CONSTANT_ACTIVITY_KEY, GROUPED_DATAFRAME, \
    RETURN_EA_COUNT_DICT_AUTOFILTER
from pm4py.util.constants import PARAM_MOST_COMMON_VARIANT
from enum import Enum
from pm4py.util import exec_utils
from copy import copy
import deprecation
from typing import Optional, Dict, Any, Union, Tuple, List
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


@deprecation.deprecated("2.2.11", "3.0.0", details="Removed")
def apply_auto_filter(df, parameters=None):
    """
    Apply auto filter on end activities

    Parameters
    -----------
    df
        Pandas dataframe
    parameters
        Parameters of the algorithm, including:
            Parameters.CASE_ID_KEY -> Case ID column in the dataframe
            Parameters.ACTIVITY_KEY -> Column that represents the activity
            Parameters.DECREASING_FACTOR -> Decreasing factor that should be passed to the algorithm

    Returns
    -----------
    df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, DEFAULT_NAME_KEY)
    grouped_df = exec_utils.get_param_value(Parameters.GROUP_DATAFRAME, parameters, None)
    return_dict = exec_utils.get_param_value(Parameters.RETURN_EA_COUNT, parameters, False)
    decreasing_factor = exec_utils.get_param_value(Parameters.DECREASING_FACTOR, parameters,
                                                   filtering_constants.DECREASING_FACTOR)

    most_common_variant = parameters[PARAM_MOST_COMMON_VARIANT] if PARAM_MOST_COMMON_VARIANT in parameters else None

    if most_common_variant is None:
        most_common_variant = []

    if len(df) > 0:
        end_activities = get_end_activities(df, parameters=parameters)
        ealist = end_activities_common.get_sorted_end_activities_list(end_activities)
        eathreshold = end_activities_common.get_end_activities_threshold(ealist, decreasing_factor)

        return filter_df_on_end_activities_nocc(df, eathreshold, ea_count0=end_activities, case_id_glue=case_id_glue,
                                                activity_key=activity_key, grouped_df=grouped_df,
                                                return_dict=return_dict,
                                                most_common_variant=most_common_variant)

    if return_dict:
        return df, {}

    return df


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
        grouped_df = df.groupby(case_id_glue)
    last_eve_df = grouped_df.last()
    last_eve_df = last_eve_df[last_eve_df[activity_key].isin(values)]
    i1 = df.set_index(case_id_glue).index
    i2 = last_eve_df.index
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
            grouped_df = df.groupby(case_id_glue)
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

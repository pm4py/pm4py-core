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
from enum import Enum
from typing import Optional, Dict, Any, Union, Tuple, List

import pandas as pd

from pm4py.statistics.traces.generic.common import case_duration as case_duration_commons
from pm4py.util import exec_utils, constants, pandas_utils
from pm4py.util import xes_constants as xes
from pm4py.util.business_hours import soj_time_business_hours_diff
from pm4py.util.constants import CASE_CONCEPT_NAME
from pm4py.util.xes_constants import DEFAULT_TIMESTAMP_KEY


class Parameters(Enum):
    ATTRIBUTE_KEY = constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY

    MAX_VARIANTS_TO_RETURN = "max_variants_to_return"
    VARIANTS_DF = "variants_df"
    ENABLE_SORT = "enable_sort"
    SORT_BY_COLUMN = "sort_by_column"
    SORT_ASCENDING = "sort_ascending"
    MAX_RET_CASES = "max_ret_cases"

    BUSINESS_HOURS = "business_hours"
    BUSINESS_HOUR_SLOTS = "business_hour_slots"
    WORKCALENDAR = "workcalendar"


def get_variant_statistics(df: pd.DataFrame, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Union[
    List[Dict[str, int]], List[Dict[List[str], int]]]:
    """
    Get variants from a Pandas dataframe

    Parameters
    -----------
    df
        Dataframe
    parameters
        Parameters of the algorithm, including:
            Parameters.CASE_ID_KEY -> Column that contains the Case ID
            Parameters.ACTIVITY_KEY -> Column that contains the activity
            Parameters.MAX_VARIANTS_TO_RETURN -> Maximum number of variants to return
            variants_df -> If provided, avoid recalculation of the variants dataframe

    Returns
    -----------
    variants_list
        List of variants inside the Pandas dataframe
    """
    if parameters is None:
        parameters = {}
    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME)

    max_variants_to_return = exec_utils.get_param_value(Parameters.MAX_VARIANTS_TO_RETURN, parameters, None)
    variants_df = exec_utils.get_param_value(Parameters.VARIANTS_DF, parameters, get_variants_df(df,
                                                                                                 parameters=parameters))

    variants_df = variants_df.reset_index()
    variants_list = pandas_utils.to_dict_records(variants_df.groupby("variant").agg("count").reset_index())
    variants_list = sorted(variants_list, key=lambda x: (x[case_id_glue], x["variant"]), reverse=True)
    if max_variants_to_return:
        variants_list = variants_list[:min(len(variants_list), max_variants_to_return)]
    return variants_list


def get_variants_df_and_list(df: pd.DataFrame, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Tuple[
    pd.DataFrame, Union[List[Dict[str, int]], List[Dict[List[str], int]]]]:
    """
    (Technical method) Provides variants_df and variants_list out of the box

    Parameters
    ------------
    df
        Dataframe
    parameters
        Parameters of the algorithm, including:
            Parameters.CASE_ID_KEY -> Column that contains the Case ID
            Parameters.ACTIVITY_KEY -> Column that contains the activity

    Returns
    ------------
    variants_df
        Variants dataframe
    variants_list
        List of variants sorted by their count
    """
    if parameters is None:
        parameters = {}
    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME)

    variants_df = get_variants_df(df, parameters=parameters)
    variants_stats = get_variant_statistics(df, parameters=parameters)
    variants_list = []
    for vd in variants_stats:
        variant = vd["variant"]
        count = vd[case_id_glue]
        variants_list.append([variant, count])
        variants_list = sorted(variants_list, key=lambda x: (x[1], x[0]), reverse=True)
    return variants_df, variants_list


def get_cases_description(df: pd.DataFrame, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Dict[
    str, Dict[str, Any]]:
    """
    Get a description of traces present in the Pandas dataframe

    Parameters
    -----------
    df
        Pandas dataframe
    parameters
        Parameters of the algorithm, including:
            Parameters.CASE_ID_KEY -> Column that identifies the case ID
            Parameters.TIMESTAMP_KEY -> Column that identifies the timestamp
            enable_sort -> Enable sorting of traces
            Parameters.SORT_BY_COLUMN -> Sort traces inside the dataframe using the specified column.
            Admitted values: startTime, endTime, caseDuration
            Parameters.SORT_ASCENDING -> Set sort direction (boolean; it true then the sort direction is ascending,
            otherwise descending)
            Parameters.MAX_RET_CASES -> Set the maximum number of returned traces

    Returns
    -----------
    ret
        Dictionary of traces associated to their start timestamp, their end timestamp and their duration
    """
    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY)
    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters, None)
    if start_timestamp_key is None:
        start_timestamp_key = timestamp_key

    enable_sort = exec_utils.get_param_value(Parameters.ENABLE_SORT, parameters, True)
    sort_by_column = exec_utils.get_param_value(Parameters.SORT_BY_COLUMN, parameters, "startTime")
    sort_ascending = exec_utils.get_param_value(Parameters.SORT_ASCENDING, parameters, True)
    max_ret_cases = exec_utils.get_param_value(Parameters.MAX_RET_CASES, parameters, None)

    business_hours = exec_utils.get_param_value(Parameters.BUSINESS_HOURS, parameters, False)
    business_hours_slots = exec_utils.get_param_value(Parameters.BUSINESS_HOUR_SLOTS, parameters, constants.DEFAULT_BUSINESS_HOUR_SLOTS)
    workcalendar = exec_utils.get_param_value(Parameters.WORKCALENDAR, parameters, constants.DEFAULT_BUSINESS_HOURS_WORKCALENDAR)

    grouped_df = df[[case_id_glue, timestamp_key]].groupby(df[case_id_glue])
    # grouped_df = df[[case_id_glue, timestamp_key]].groupby(df[case_id_glue])
    first_eve_df = grouped_df.first()
    last_eve_df = grouped_df.last()
    del grouped_df
    last_eve_df.columns = [str(col) + '_2' for col in first_eve_df.columns]
    stacked_df = pd.concat([first_eve_df, last_eve_df], axis=1)
    del first_eve_df
    del last_eve_df
    del stacked_df[case_id_glue]
    del stacked_df[case_id_glue + "_2"]

    if business_hours:
        stacked_df['caseDuration'] = stacked_df.apply(
            lambda x: soj_time_business_hours_diff(x[start_timestamp_key], x[timestamp_key + "_2"], business_hours_slots, workcalendar), axis=1)
    else:
        stacked_df['caseDuration'] = stacked_df[timestamp_key + "_2"] - stacked_df[start_timestamp_key]
        stacked_df['caseDuration'] = stacked_df['caseDuration'].dt.total_seconds()

    stacked_df[timestamp_key + "_2"] = stacked_df[timestamp_key + "_2"].astype('int64') // 10 ** 9
    stacked_df[start_timestamp_key] = stacked_df[start_timestamp_key].astype('int64') // 10 ** 9
    stacked_df = stacked_df.rename(columns={start_timestamp_key: 'startTime', timestamp_key + "_2": 'endTime'})
    if enable_sort:
        stacked_df = stacked_df.sort_values(sort_by_column, ascending=sort_ascending)

    if max_ret_cases is not None:
        stacked_df = stacked_df.head(n=min(max_ret_cases, len(stacked_df)))
    ret = pandas_utils.to_dict_index(stacked_df)
    return ret


def get_variants_df(df, parameters=None):
    """
    Get variants dataframe from a Pandas dataframe

    Parameters
    -----------
    df
        Dataframe
    parameters
        Parameters of the algorithm, including:
            Parameters.CASE_ID_KEY -> Column that contains the Case ID
            Parameters.ACTIVITY_KEY -> Column that contains the activity

    Returns
    -----------
    variants_df
        Variants dataframe
    """
    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes.DEFAULT_NAME_KEY)

    new_df = df.groupby(case_id_glue, sort=False)[activity_key].agg(lambda col: tuple(pd.Series.to_list(col))).to_frame()

    new_cols = list(new_df.columns)
    new_df = new_df.rename(columns={new_cols[0]: "variant"})

    return new_df


def get_variants_df_with_case_duration(df, parameters=None):
    """
    Get variants dataframe from a Pandas dataframe, with case duration that is included

    Parameters
    -----------
    df
        Dataframe
    parameters
        Parameters of the algorithm, including:
            Parameters.CASE_ID_KEY -> Column that contains the Case ID
            Parameters.ACTIVITY_KEY -> Column that contains the activity
            Parameters.TIMESTAMP_KEY -> Column that contains the timestamp

    Returns
    -----------
    variants_df
        Variants dataframe
    """
    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY)

    business_hours = exec_utils.get_param_value(Parameters.BUSINESS_HOURS, parameters, False)
    business_hours_slots = exec_utils.get_param_value(Parameters.BUSINESS_HOUR_SLOTS, parameters, constants.DEFAULT_BUSINESS_HOUR_SLOTS)

    workcalendar = exec_utils.get_param_value(Parameters.WORKCALENDAR, parameters, constants.DEFAULT_BUSINESS_HOURS_WORKCALENDAR)

    grouped_df = df[[case_id_glue, timestamp_key, activity_key]].groupby(df[case_id_glue])

    df1 = grouped_df[activity_key].agg(lambda col: tuple(pd.Series.to_list(col))).to_frame()
    new_cols = list(df1.columns)
    df1 = df1.rename(columns={new_cols[0]: "variant"})

    first_eve_df = grouped_df.first()
    last_eve_df = grouped_df.last()
    del grouped_df
    last_eve_df.columns = [str(col) + '_2' for col in first_eve_df.columns]
    stacked_df = pd.concat([first_eve_df, last_eve_df], axis=1)
    del first_eve_df
    del last_eve_df
    del stacked_df[case_id_glue]
    del stacked_df[case_id_glue + "_2"]
    stacked_df['caseDuration'] = stacked_df[timestamp_key + "_2"] - stacked_df[timestamp_key]
    stacked_df['caseDuration'] = stacked_df['caseDuration'].dt.total_seconds()
    if business_hours:
        stacked_df['caseDuration'] = stacked_df.apply(
            lambda x: soj_time_business_hours_diff(x[timestamp_key], x[timestamp_key + "_2"], business_hours_slots, workcalendar), axis=1)
    else:
        stacked_df['caseDuration'] = stacked_df[timestamp_key + "_2"] - stacked_df[timestamp_key]
        stacked_df['caseDuration'] = stacked_df['caseDuration'].dt.total_seconds()
    new_df = pd.concat([df1, stacked_df], axis=1)
    del df1
    del stacked_df
    return new_df


def get_events(df: pd.DataFrame, case_id: str, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> List[
    Dict[str, Any]]:
    """
    Get events belonging to the specified case

    Parameters
    -----------
    df
        Pandas dataframe
    case_id
        Required case ID
    parameters
        Possible parameters of the algorithm, including:
            Parameters.CASE_ID_KEY -> Column in which the case ID is contained

    Returns
    ----------
    list_eve
        List of events belonging to the case
    """
    if parameters is None:
        parameters = {}
    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME)

    return pandas_utils.to_dict_records(df[df[case_id_glue] == case_id])


def get_kde_caseduration(df, parameters=None):
    """
    Gets the estimation of KDE density for the case durations calculated on the dataframe

    Parameters
    --------------
    df
        Pandas dataframe
    parameters
        Possible parameters of the algorithm, including:
            Parameters.GRAPH_POINTS -> number of points to include in the graph
            Parameters.CASE_ID_KEY -> Column hosting the Case ID


    Returns
    --------------
    x
        X-axis values to represent
    y
        Y-axis values to represent
    """
    cases = get_cases_description(df, parameters=parameters)
    duration_values = [x["caseDuration"] for x in cases.values()]

    return case_duration_commons.get_kde_caseduration(duration_values, parameters=parameters)


def get_kde_caseduration_json(df, parameters=None):
    """
    Gets the estimation of KDE density for the case durations calculated on the log/dataframe
    (expressed as JSON)

    Parameters
    --------------
    df
        Pandas dataframe
    parameters
        Possible parameters of the algorithm, including:
            Parameters.GRAPH_POINTS -> number of points to include in the graph
            Parameters.CASE_ID_KEY -> Column hosting the Case ID

    Returns
    --------------
    json
        JSON representing the graph points
    """
    cases = get_cases_description(df, parameters=parameters)
    duration_values = [x["caseDuration"] for x in cases.values()]

    return case_duration_commons.get_kde_caseduration_json(duration_values, parameters=parameters)


def get_all_case_durations(df, parameters=None):
    """
    Gets all the case durations out of the log

    Parameters
    ------------
    df
        Pandas dataframe
    parameters
        Possible parameters of the algorithm

    Returns
    ------------
    duration_values
        List of all duration values
    """
    cd = get_cases_description(df, parameters=parameters)
    durations = [y["caseDuration"] for y in cd.values()]
    return sorted(durations)


def get_first_quartile_case_duration(df, parameters=None):
    """
    Gets the first quartile out of the log

    Parameters
    -------------
    df
        Pandas dataframe
    parameters
        Possible parameters of the algorithm

    Returns
    -------------
    value
        First quartile value
    """
    if parameters is None:
        parameters = {}

    duration_values = get_all_case_durations(df, parameters=parameters)
    if duration_values:
        return duration_values[int((len(duration_values) * 3) / 4)]
    return 0


def get_median_case_duration(df, parameters=None):
    """
    Gets the median case duration out of the log

    Parameters
    -------------
    df
        Pandas dataframe
    parameters
        Possible parameters of the algorithm

    Returns
    -------------
    value
        Median duration value
    """
    if parameters is None:
        parameters = {}

    duration_values = get_all_case_durations(df, parameters=parameters)
    if duration_values:
        return duration_values[int(len(duration_values) / 2)]
    return 0

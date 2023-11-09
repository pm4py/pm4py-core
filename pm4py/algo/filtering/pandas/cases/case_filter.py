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
from pm4py.util import constants, xes_constants
from enum import Enum
from pm4py.util import exec_utils
from copy import copy
from typing import Optional, Dict, Any, Union
import pandas as pd
from pm4py.util.business_hours import soj_time_business_hours_diff


class Parameters(Enum):
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY

    BUSINESS_HOURS = "business_hours"
    BUSINESS_HOUR_SLOTS = "business_hour_slots"
    WORKCALENDAR = "workcalendar"


def filter_on_ncases(df: pd.DataFrame, case_id_glue: str = constants.CASE_CONCEPT_NAME, max_no_cases: int = 1000):
    """
    Filter a dataframe keeping only the specified maximum number of traces

    Parameters
    -----------
    df
        Dataframe
    case_id_glue
        Case ID column in the CSV
    max_no_cases
        Maximum number of traces to keep

    Returns
    ------------
    df
        Filtered dataframe
    """
    cases_values_dict = dict(df[case_id_glue].value_counts())
    cases_to_keep = []
    for case in cases_values_dict:
        cases_to_keep.append(case)
    cases_to_keep = cases_to_keep[0:min(len(cases_to_keep), max_no_cases)]
    ret = df[df[case_id_glue].isin(cases_to_keep)]
    ret.attrs = copy(df.attrs) if hasattr(df, 'attrs') else {}
    return ret


def filter_on_case_size(df0: pd.DataFrame, case_id_glue: str = "case:concept:name", min_case_size: int = 2, max_case_size=None):
    """
    Filter a dataframe keeping only traces with at least the specified number of events

    Parameters
    -----------
    df
        Dataframe
    case_id_glue
        Case ID column in the CSV
    min_case_size
        Minimum size of a case
    max_case_size
        Maximum case size

    Returns
    -----------
    df
        Filtered dataframe
    """
    df = df0.copy()
    element_group_size = df[case_id_glue].groupby(df[case_id_glue]).transform('size')
    df = df[element_group_size >= min_case_size]
    if max_case_size is not None:
        df = df[element_group_size <= max_case_size]
    df.attrs = copy(df0.attrs) if hasattr(df0, 'attrs') else {}
    return df


def filter_on_case_performance(df: pd.DataFrame, case_id_glue: str = constants.CASE_CONCEPT_NAME,
                               timestamp_key: str = xes_constants.DEFAULT_TIMESTAMP_KEY,
                               min_case_performance: float = 0, max_case_performance: float = 10000000000,
                               business_hours=False, business_hours_slots=constants.DEFAULT_BUSINESS_HOUR_SLOTS) -> pd.DataFrame:
    """
    Filter a dataframe on case performance

    Parameters
    -----------
    df
        Dataframe
    case_id_glue
        Case ID column in the CSV
    timestamp_key
        Timestamp column to use for the CSV
    min_case_performance
        Minimum case performance
    max_case_performance
        Maximum case performance

    Returns
    -----------
    df
        Filtered dataframe
    """
    grouped_df = df[[case_id_glue, timestamp_key]].groupby(df[case_id_glue])
    start_events = grouped_df.first()
    end_events = grouped_df.last()
    end_events.columns = [str(col) + '_2' for col in end_events.columns]
    stacked_df = pd.concat([start_events, end_events], axis=1)
    if business_hours:
        stacked_df['caseDuration'] = stacked_df.apply(
            lambda x: soj_time_business_hours_diff(x[timestamp_key], x[timestamp_key + "_2"], business_hours_slots), axis=1)
    else:
        stacked_df['caseDuration'] = stacked_df[timestamp_key + "_2"] - stacked_df[timestamp_key]
        stacked_df['caseDuration'] = stacked_df['caseDuration'].dt.total_seconds()
    stacked_df = stacked_df[stacked_df['caseDuration'] <= max_case_performance]
    stacked_df = stacked_df[stacked_df['caseDuration'] >= min_case_performance]
    i1 = df.set_index(case_id_glue).index
    i2 = stacked_df.set_index(case_id_glue).index
    ret = df[i1.isin(i2)]
    ret.attrs = copy(df.attrs) if hasattr(df, 'attrs') else {}
    return ret


def filter_case_performance(df: pd.DataFrame, min_case_performance: float = 0, max_case_performance: float = 10000000000, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> pd.DataFrame:
    if parameters is None:
        parameters = {}
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    case_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
    business_hours = exec_utils.get_param_value(Parameters.BUSINESS_HOURS, parameters, False)
    business_hours_slots = exec_utils.get_param_value(Parameters.BUSINESS_HOUR_SLOTS, parameters, constants.DEFAULT_BUSINESS_HOUR_SLOTS)

    return filter_on_case_performance(df, min_case_performance=min_case_performance,
                                      max_case_performance=max_case_performance, timestamp_key=timestamp_key,
                                      case_id_glue=case_glue, business_hours=business_hours, business_hours_slots=business_hours_slots)


def apply(df, parameters=None):
    del df
    del parameters
    raise NotImplementedError("apply method not available for case filter")


def apply_auto_filter(df, parameters=None):
    del df
    del parameters
    raise Exception("apply_auto_filter method not available for case filter")

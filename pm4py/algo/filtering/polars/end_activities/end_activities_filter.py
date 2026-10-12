'''
PM4Py – A Process Mining Library for Python
Copyright (C) 2026 Process Intelligence Solutions GmbH

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see this software project's root or
visit <https://www.gnu.org/licenses/>.

Website: https://processintelligence.solutions
Contact: info@processintelligence.solutions
'''
from pm4py.util.constants import CASE_CONCEPT_NAME
from pm4py.util import xes_constants as xes
from pm4py.util.xes_constants import DEFAULT_NAME_KEY
from pm4py.util.constants import (
    PARAMETER_CONSTANT_CASEID_KEY,
    PARAMETER_CONSTANT_ACTIVITY_KEY,
    GROUPED_DATAFRAME,
    RETURN_EA_COUNT_DICT_AUTOFILTER,
)
from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any, Union, List
import polars as pl


class Parameters(Enum):
    CASE_ID_KEY = PARAMETER_CONSTANT_CASEID_KEY
    ACTIVITY_KEY = PARAMETER_CONSTANT_ACTIVITY_KEY
    DECREASING_FACTOR = "decreasingFactor"
    GROUP_DATAFRAME = GROUPED_DATAFRAME
    POSITIVE = "positive"
    RETURN_EA_COUNT = RETURN_EA_COUNT_DICT_AUTOFILTER


def get_end_activities(
    df: pl.LazyFrame,
    case_id_key: str = CASE_CONCEPT_NAME,
    activity_key: str = DEFAULT_NAME_KEY,
    parameters: Optional[Dict[Any, Any]] = None,
) -> Dict[str, int]:
    """
    Get end activities from a LazyFrame with their counts

    Parameters
    ----------
    df
        LazyFrame
    case_id_key
        Case ID column
    activity_key
        Activity column
    parameters
        Parameters

    Returns
    ----------
    end_activities_dict
        Dictionary of end activities and their counts
    """
    if parameters is None:
        parameters = {}

    # Get last activity for each case
    end_activities = (
        df.group_by(case_id_key)
        .agg(pl.col(activity_key).last().alias("end_activity"))
        .group_by("end_activity")
        .len(name="count")
        .collect()
    )

    # Convert to dictionary
    result = {}
    for row in end_activities.iter_rows():
        result[row[0]] = row[1]

    return result


def apply(
    df: pl.LazyFrame,
    values: List[str],
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> pl.LazyFrame:
    """
    Filter LazyFrame on end activities

    Parameters
    ----------
    df
        LazyFrame
    values
        Values to filter on
    parameters
        Possible parameters of the algorithm, including:
            Parameters.CASE_ID_KEY -> Case ID column in the LazyFrame
            Parameters.ACTIVITY_KEY -> Column that represents the activity
            Parameters.POSITIVE -> Specifies if the filtered should be applied including traces (positive=True)
            or excluding traces (positive=False)

    Returns
    ----------
    df
        Filtered LazyFrame
    """
    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME
    )
    activity_key = exec_utils.get_param_value(
        Parameters.ACTIVITY_KEY, parameters, DEFAULT_NAME_KEY
    )
    positive = exec_utils.get_param_value(
        Parameters.POSITIVE, parameters, True
    )

    return filter_df_on_end_activities(
        df,
        values,
        case_id_glue=case_id_glue,
        activity_key=activity_key,
        positive=positive,
    )


def filter_df_on_end_activities(
    df: pl.LazyFrame,
    values: List[str],
    case_id_glue: str = CASE_CONCEPT_NAME,
    activity_key: str = xes.DEFAULT_NAME_KEY,
    positive: bool = True,
) -> pl.LazyFrame:
    """
    Filter LazyFrame on end activities

    Parameters
    ----------
    df
        LazyFrame
    values
        Values to filter on
    case_id_glue
        Case ID column in the LazyFrame
    activity_key
        Column that represent the activity
    positive
        Specifies if the filtered should be applied including traces (positive=True) or excluding traces
        (positive=False)

    Returns
    ----------
    df
        Filtered LazyFrame
    """
    # Get cases with matching end activities
    matching_cases = (
        df.group_by(case_id_glue)
        .agg(pl.col(activity_key).last().alias("end_activity"))
        .filter(pl.col("end_activity").is_in(values))
        .select(case_id_glue)
    )

    if positive:
        # Keep cases with matching end activities
        ret = df.join(matching_cases, on=case_id_glue, how="inner", maintain_order="left")
    else:
        # Keep cases without matching end activities
        ret = df.join(matching_cases, on=case_id_glue, how="anti", maintain_order="left")

    return ret


def filter_df_on_end_activities_nocc(
    df: pl.LazyFrame,
    nocc: int,
    ea_count0: Optional[Dict[str, int]] = None,
    case_id_glue: str = CASE_CONCEPT_NAME,
    activity_key: str = xes.DEFAULT_NAME_KEY,
    return_dict: bool = False,
    most_common_variant: Optional[List[str]] = None,
):
    """
    Filter LazyFrame on end activities number of occurrences

    Parameters
    -----------
    df
        LazyFrame
    nocc
        Minimum number of occurrences of the end activity
    ea_count0
        (if provided) Dictionary that associates each end activity with its count
    case_id_glue
        Column that contains the Case ID
    activity_key
        Column that contains the activity
    return_dict
        Return dict
    most_common_variant
        Most common variant (if provided)
    """
    if most_common_variant is None:
        most_common_variant = []

    if ea_count0 is None:
        ea_count0 = get_end_activities(df, case_id_glue, activity_key)

    ea_count = [
        k
        for k, v in ea_count0.items()
        if v >= nocc
        or (len(most_common_variant) > 0 and k == most_common_variant[-1])
    ]
    ea_count_dict = {
        k: v
        for k, v in ea_count0.items()
        if v >= nocc
        or (len(most_common_variant) > 0 and k == most_common_variant[-1])
    }

    if len(ea_count) < len(ea_count0):
        ret = filter_df_on_end_activities(
            df, ea_count, case_id_glue=case_id_glue, activity_key=activity_key
        )
        if return_dict:
            return ret, ea_count_dict
        return ret

    if return_dict:
        return df, ea_count_dict
    return df
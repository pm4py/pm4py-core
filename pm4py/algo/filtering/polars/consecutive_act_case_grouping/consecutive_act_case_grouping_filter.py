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
import polars as pl
from typing import Optional, Dict, Any
from pm4py.util import constants, xes_constants, exec_utils
from enum import Enum


class Parameters(Enum):
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    FILTER_TYPE = "filter_type"


def apply(
    df: pl.LazyFrame,
    parameters: Optional[Dict[Any, Any]] = None,
) -> pl.LazyFrame:
    """
    Groups the consecutive events of the same case having the same activity, providing option to keep the first/last event of each group

    Parameters
    ---------------
    df
        Polars LazyFrame
    parameters
        Parameters of the algorithm, including:

        - Parameters.CASE_ID_KEY => the case identifier to be used
        - Parameters.ACTIVITY_KEY => the attribute to be used as activity
        - Parameters.FILTER_TYPE => the type of filter to be applied:
            * first => keeps the first event of each group
            * last => keeps the last event of each group

    Returns
    ---------------
    filtered_dataframe
        Filtered LazyFrame
    """
    if parameters is None:
        parameters = {}

    case_id_key = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME
    )
    activity_key = exec_utils.get_param_value(
        Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY
    )
    filter_type = exec_utils.get_param_value(
        Parameters.FILTER_TYPE, parameters, "first"
    )

    # Add row number to maintain order
    df = df.with_row_index("_row_num")

    # Create a column that changes when case or activity changes
    df = df.with_columns(
        (
            (pl.col(case_id_key) != pl.col(case_id_key).shift(1)) |
            (pl.col(activity_key) != pl.col(activity_key).shift(1))
        ).fill_null(True).cum_sum().alias("_group_id")
    )

    if filter_type == "first":
        # Keep first event of each group
        df = df.group_by("_group_id").agg(pl.all().first()).sort("_row_num")
    elif filter_type == "last":
        # Keep last event of each group
        df = df.group_by("_group_id").agg(pl.all().last()).sort("_row_num")

    # Remove helper columns
    df = df.drop(["_row_num", "_group_id"])

    return df

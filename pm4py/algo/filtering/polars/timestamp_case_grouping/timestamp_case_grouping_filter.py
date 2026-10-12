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
from pm4py.util.constants import CASE_CONCEPT_NAME, PARAMETER_CONSTANT_CASEID_KEY, PARAMETER_CONSTANT_TIMESTAMP_KEY, PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.util.xes_constants import DEFAULT_TIMESTAMP_KEY, DEFAULT_NAME_KEY
from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any, Union
import polars as pl


class Parameters(Enum):
    CASE_ID_KEY = PARAMETER_CONSTANT_CASEID_KEY
    ACTIVITY_KEY = PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = PARAMETER_CONSTANT_TIMESTAMP_KEY
    FILTER_TYPE = "filter_type"


def apply(
    df: pl.LazyFrame,
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> pl.LazyFrame:
    """
    Groups the events of the same case happening at the same timestamp,
    providing option to keep the first event of each group, keep the last event of each group, create an event
    having as activity the concatenation of the activities happening in the group

    Parameters
    -----------
    df
        LazyFrame
    parameters
        Parameters of the algorithm, including:

        - Parameters.CASE_ID_KEY => the case identifier to be used
        - Parameters.ACTIVITY_KEY => the attribute to be used as activity
        - Parameters.TIMESTAMP_KEY => the attribute to be used as timestamp
        - Parameters.FILTER_TYPE => the type of filter to be applied:
            * first => keeps the first event of each group
            * last => keeps the last event of each group
            * concat => creates an event having as activity the concatenation of the activities happening in the group

    Returns
    -----------
    df
        Filtered LazyFrame
    """
    if parameters is None:
        parameters = {}

    case_id_key = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME
    )
    timestamp_key = exec_utils.get_param_value(
        Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY
    )
    activity_key = exec_utils.get_param_value(
        Parameters.ACTIVITY_KEY, parameters, DEFAULT_NAME_KEY
    )
    filter_type = exec_utils.get_param_value(
        Parameters.FILTER_TYPE, parameters, "first"
    )

    if filter_type == "first":
        # Keep first event of each group
        df = df.group_by([case_id_key, timestamp_key], maintain_order=True).first()
    elif filter_type == "last":
        # Keep last event of each group
        df = df.group_by([case_id_key, timestamp_key], maintain_order=True).last()
    elif filter_type == "concat":
        # Get all columns except activity for the first event, then concatenate activities
        # First, get the grouped dataframe
        grouped = df.group_by([case_id_key, timestamp_key], maintain_order=True)

        # Get all columns from first event
        first_df = grouped.first()

        # Get concatenated activities
        concat_activities = grouped.agg(
            pl.col(activity_key).sort().str.join(" & ").alias(activity_key)
        )

        # Update the activity column in first_df with concatenated values
        df = first_df.drop(activity_key).join(
            concat_activities,
            on=[case_id_key, timestamp_key],
            how="left",
            maintain_order="left",
        )

    return df
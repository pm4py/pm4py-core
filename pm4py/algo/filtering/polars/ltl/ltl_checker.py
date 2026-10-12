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
from enum import Enum
from pm4py.util import exec_utils, constants
from pm4py.util.constants import CASE_CONCEPT_NAME
from pm4py.util.constants import (
    PARAMETER_CONSTANT_ATTRIBUTE_KEY,
    PARAMETER_CONSTANT_CASEID_KEY,
    PARAMETER_CONSTANT_RESOURCE_KEY,
    PARAMETER_CONSTANT_TIMESTAMP_KEY,
)
from pm4py.util.xes_constants import (
    DEFAULT_NAME_KEY,
    DEFAULT_RESOURCE_KEY,
    DEFAULT_TIMESTAMP_KEY,
)
from typing import Optional, Dict, Any, Union, List
import polars as pl


class Parameters(Enum):
    CASE_ID_KEY = PARAMETER_CONSTANT_CASEID_KEY
    ATTRIBUTE_KEY = PARAMETER_CONSTANT_ATTRIBUTE_KEY
    TIMESTAMP_KEY = PARAMETER_CONSTANT_TIMESTAMP_KEY
    RESOURCE_KEY = PARAMETER_CONSTANT_RESOURCE_KEY
    POSITIVE = "positive"
    ENABLE_TIMESTAMP = "enable_timestamp"
    TIMESTAMP_DIFF_BOUNDARIES = "timestamp_diff_boundaries"


def eventually_follows(
    df: pl.LazyFrame,
    attribute_values: List[str],
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> pl.LazyFrame:
    """
    Applies the eventually follows rule

    Parameters
    ------------
    df
        LazyFrame
    attribute_values
        A list of attribute_values attribute_values[n] follows attribute_values[n-1] follows ... follows attribute_values[0]

    parameters
        Parameters of the algorithm, including the attribute key and the positive parameter:
        - If True, returns all the cases containing all attribute_values and in which attribute_values[i] was eventually followed by attribute_values[i + 1]
        - If False, returns all the cases not containing all attribute_values, or in which an instance of attribute_values[i] was not eventually
        followed by an instance of attribute_values[i + 1]

    Returns
    ------------
    filtered_df
        Filtered LazyFrame
    """
    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME
    )
    attribute_key = exec_utils.get_param_value(
        Parameters.ATTRIBUTE_KEY, parameters, DEFAULT_NAME_KEY
    )
    timestamp_key = exec_utils.get_param_value(
        Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY
    )
    positive = exec_utils.get_param_value(
        Parameters.POSITIVE, parameters, True
    )

    # Add row numbers within each case for ordering
    df = df.sort([case_id_glue, timestamp_key], maintain_order=True).with_columns(
        pl.int_range(pl.len()).over(case_id_glue).alias("_index")
    )

    # Get cases that contain all required activities
    cases_with_all = df
    for attr_val in attribute_values:
        attr_cases = (
            df.filter(pl.col(attribute_key) == attr_val)
            .select(case_id_glue)
            .unique()
        )
        cases_with_all = cases_with_all.join(attr_cases, on=case_id_glue, how="inner", maintain_order="left")

    # Check the ordering constraint
    valid_cases = cases_with_all.select(case_id_glue).unique()

    for i in range(len(attribute_values) - 1):
        curr_val = attribute_values[i]
        next_val = attribute_values[i + 1]

        # Get events for current and next values
        curr_events = df.filter(pl.col(attribute_key) == curr_val).select([
            case_id_glue, "_index", timestamp_key
        ])
        next_events = df.filter(pl.col(attribute_key) == next_val).select([
            case_id_glue, "_index", timestamp_key
        ])

        # Join and check ordering
        ordered_pairs = (
            curr_events.join(next_events, on=case_id_glue, suffix="_next", maintain_order="left")
            .filter(pl.col("_index") < pl.col("_index_next"))
            .select(case_id_glue)
            .unique()
        )

        valid_cases = valid_cases.join(ordered_pairs, on=case_id_glue, how="inner", maintain_order="left")

    # Apply positive/negative filter
    if positive:
        ret = df.join(valid_cases, on=case_id_glue, how="inner", maintain_order="left")
    else:
        ret = df.join(valid_cases, on=case_id_glue, how="anti", maintain_order="left")

    # Remove helper columns
    ret = ret.drop("_index")

    return ret


def A_next_B_next_C(
    df: pl.LazyFrame,
    attribute_values: List[str],
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> pl.LazyFrame:
    """
    Applies the A next B next C rule

    Parameters
    ------------
    df
        LazyFrame
    attribute_values
        A list of attribute_values attribute_values[n] follows attribute_values[n-1] follows ... follows attribute_values[0]

    parameters
        Parameters of the algorithm, including the attribute key and the positive parameter:
        - If True, returns all the cases containing all attribute_values and in which attribute_values[i] is directly followed by attribute_values[i + 1]
        - If False, returns all the cases not containing all attribute_values, or in which an instance of attribute_values[i] is not directly followed by an instance
        of attribute_values[i + 1]

    Returns
    ------------
    filtered_df
        Filtered LazyFrame
    """
    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME
    )
    attribute_key = exec_utils.get_param_value(
        Parameters.ATTRIBUTE_KEY, parameters, DEFAULT_NAME_KEY
    )
    timestamp_key = exec_utils.get_param_value(
        Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY
    )
    positive = exec_utils.get_param_value(
        Parameters.POSITIVE, parameters, True
    )

    # Add row numbers within each case
    df = df.sort([case_id_glue, timestamp_key], maintain_order=True).with_columns(
        pl.int_range(pl.len()).over(case_id_glue).alias("_pos")
    )

    # Create the pattern to match
    pattern_length = len(attribute_values)

    # For each case, check if the pattern exists
    valid_cases = []

    # This is a simplified implementation - for production use, 
    # a more efficient sliding window approach would be better
    df_collected = df.collect()

    for case_id in df_collected[case_id_glue].unique():
        case_df = df_collected.filter(pl.col(case_id_glue) == case_id).sort("_pos")
        activities = case_df[attribute_key].to_list()

        # Check if pattern exists in sequence
        pattern_found = False
        for i in range(len(activities) - pattern_length + 1):
            if activities[i:i + pattern_length] == attribute_values:
                pattern_found = True
                break

        if pattern_found:
            valid_cases.append(case_id)

    # Convert back to LazyFrame
    valid_cases_df = pl.DataFrame({case_id_glue: valid_cases}).lazy()

    if positive:
        ret = df.join(valid_cases_df, on=case_id_glue, how="inner", maintain_order="left")
    else:
        ret = df.join(valid_cases_df, on=case_id_glue, how="anti", maintain_order="left")

    # Remove helper columns
    ret = ret.drop("_pos")

    return ret


def four_eyes_principle(
    df: pl.LazyFrame,
    attribute_values: List[str],
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> pl.LazyFrame:
    """
    Verifies the Four Eyes Principle given a set of activities

    Parameters
    -------------
    df
        LazyFrame
    attribute_values
        List of activities to verify
    parameters
        Parameters of the algorithm, including the attribute key and the positive parameter:
        - if True, then filters all the cases where the resource executing each activity is DIFFERENT from the others
        - if False, then filters all the cases where at least one pair of activities is executed by the SAME resource

    Returns
    --------------
    filtered_df
        Filtered LazyFrame
    """
    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME
    )
    attribute_key = exec_utils.get_param_value(
        Parameters.ATTRIBUTE_KEY, parameters, DEFAULT_NAME_KEY
    )
    resource_key = exec_utils.get_param_value(
        Parameters.RESOURCE_KEY, parameters, DEFAULT_RESOURCE_KEY
    )
    positive = exec_utils.get_param_value(
        Parameters.POSITIVE, parameters, True
    )

    if len(attribute_values) < 2:
        return df

    # For each case, check if activities are performed by different resources
    valid_cases = None

    for i in range(len(attribute_values)):
        for j in range(i + 1, len(attribute_values)):
            act1 = attribute_values[i]
            act2 = attribute_values[j]

            # Get resources for both activities
            df1 = df.filter(pl.col(attribute_key) == act1).select([
                case_id_glue, resource_key
            ]).unique()

            df2 = df.filter(pl.col(attribute_key) == act2).select([
                case_id_glue, resource_key
            ]).unique()

            # Join to find all combinations of resources for these activities
            pairs = df1.join(df2, on=case_id_glue, suffix="_2", maintain_order="left")

            if positive:
                # For positive, we want ALL pairs to have different resources
                # So we check if ANY pair has the same resource and exclude those cases
                same_resource_cases = pairs.filter(
                    pl.col(resource_key) == pl.col(resource_key + "_2")
                ).select(case_id_glue).unique()

                # Get all cases that have both activities
                all_cases_with_both = pairs.select(case_id_glue).unique()

                # Valid cases are those that have both activities but no same resource
                valid_pairs = all_cases_with_both.join(
                    same_resource_cases, on=case_id_glue, how="anti",
                    maintain_order="left",
                )
            else:
                # For negative, we want at least ONE pair with the same resource
                valid_pairs = pairs.filter(
                    pl.col(resource_key) == pl.col(resource_key + "_2")
                ).select(case_id_glue).unique()

            if valid_cases is None:
                valid_cases = valid_pairs
            else:
                valid_cases = valid_cases.join(valid_pairs, on=case_id_glue, how="inner", maintain_order="left")

    ret = df.join(valid_cases, on=case_id_glue, how="inner", maintain_order="left")

    return ret


def attr_value_different_persons(
    df: pl.LazyFrame,
    attribute_value: str,
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> pl.LazyFrame:
    """
    Checks whether an attribute value is performed by different persons

    Parameters
    ------------
    df
        LazyFrame
    attribute_value
        Attribute value to check
    parameters
        Parameters of the algorithm, including the attribute key and the positive parameter:
            - if True, then filters all the cases where the attribute value is performed by different resources
            - if False, then filters all the cases where the attribute value is performed only by a single resource

    Returns
    -------------
    filtered_df
        Filtered LazyFrame
    """
    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME
    )
    attribute_key = exec_utils.get_param_value(
        Parameters.ATTRIBUTE_KEY, parameters, DEFAULT_NAME_KEY
    )
    resource_key = exec_utils.get_param_value(
        Parameters.RESOURCE_KEY, parameters, DEFAULT_RESOURCE_KEY
    )
    positive = exec_utils.get_param_value(
        Parameters.POSITIVE, parameters, True
    )

    # Get cases where the attribute value occurs with different resources
    resource_counts = (
        df.filter(pl.col(attribute_key) == attribute_value)
        .group_by([case_id_glue, resource_key])
        .len(name="count")
        .group_by(case_id_glue)
        .len(name="count")
        .rename({"count": "unique_resources"})
    )

    if positive:
        # Keep cases with multiple resources
        valid_cases = resource_counts.filter(
            pl.col("unique_resources") > 1
        ).select(case_id_glue)
    else:
        # Keep cases with single resource
        valid_cases = resource_counts.filter(
            pl.col("unique_resources") == 1
        ).select(case_id_glue)

    ret = df.join(valid_cases, on=case_id_glue, how="inner", maintain_order="left")

    return ret
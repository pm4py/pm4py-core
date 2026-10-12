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
from typing import Optional, Dict, Any, Union, List

import polars as pl

from pm4py.util import exec_utils, constants, xes_constants


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    SUBCASE_CONCAT_STR = "subcase_concat_str"


def apply(
    df: pl.LazyFrame,
    act1: Union[str, List[str]],
    act2: Union[str, List[str]],
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> pl.LazyFrame:
    """
    Given a LazyFrame, filters all the subtraces going from an event with activity "act1" to an event with
    activity "act2"

    Parameters
    ----------------
    df
        LazyFrame
    act1
        First activity (or collection of activities)
    act2
        Second activity (or collection of activities)
    parameters
        Parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY => activity key
        - Parameters.CASE_ID_KEY => case id
        - Parameters.SUBCASE_CONCAT_STR => concatenator between the case id and the subtrace index in the filtered df

    Returns
    ----------------
    filtered_df
        LazyFrame with all the subtraces going from "act1" to "act2"
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(
        Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY
    )
    case_id_key = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME
    )
    subcase_concat_str = exec_utils.get_param_value(
        Parameters.SUBCASE_CONCAT_STR, parameters, "##@@"
    )

    act1_list = [act1] if isinstance(act1, str) else act1
    act2_list = [act2] if isinstance(act2, str) else act2

    # Sort by case and timestamp
    df = df.sort([case_id_key, xes_constants.DEFAULT_TIMESTAMP_KEY], maintain_order=True)

    # Add row number within each case
    df = df.with_columns(
        pl.int_range(pl.len()).over(case_id_key).alias("_event_idx")
    )

    # Mark activities
    df = df.with_columns([
        pl.col(activity_key).is_in(act1_list).alias("_is_act1"),
        pl.col(activity_key).is_in(act2_list).alias("_is_act2")
    ])

    # For each act1, find the next act2 and create a segment identifier
    df = df.with_columns([
        # Mark positions where act1 occurs
        pl.when(pl.col("_is_act1"))
        .then(pl.col("_event_idx"))
        .otherwise(None)
        .alias("_act1_pos"),

        # Mark positions where act2 occurs  
        pl.when(pl.col("_is_act2"))
        .then(pl.col("_event_idx"))
        .otherwise(None)
        .alias("_act2_pos")
    ])

    # For each event, find the most recent act1 position before it
    df = df.with_columns(
        pl.col("_act1_pos")
        .fill_null(strategy="forward")
        .over(case_id_key)
        .alias("_current_act1")
    )

    # Mark events that are part of a valid segment (between act1 and act2 inclusive)
    df = df.with_columns(
        # An event is in a segment if:
        # 1. There's a current act1 before or at this position
        # 2. Either it's the act1 itself, or it's after act1 but before or at the next act2
        pl.when(
            pl.col("_current_act1").is_not_null() & 
            (pl.col("_event_idx") >= pl.col("_current_act1"))
        )
        .then(pl.col("_current_act1"))
        .otherwise(None)
        .alias("_segment_start")
    )

    # Find segment ends (act2 positions that have a preceding act1)
    df = df.with_columns(
        pl.when(
            pl.col("_is_act2") & 
            pl.col("_segment_start").is_not_null()
        )
        .then(pl.col("_event_idx"))
        .otherwise(None)
        .alias("_segment_end")
    )

    # For each segment end, we need to create a subcase
    # First, mark segment boundaries
    df = df.with_columns(
        pl.col("_segment_end")
        .fill_null(strategy="backward") 
        .over(case_id_key)
        .alias("_next_segment_end")
    )

    # Keep only events that are in complete segments
    df = df.filter(
        pl.col("_segment_start").is_not_null() &
        pl.col("_next_segment_end").is_not_null() &
        (pl.col("_event_idx") <= pl.col("_next_segment_end"))
    )

    # Create unique segment identifiers
    df = df.with_columns(
        # Create a unique identifier for each segment
        (pl.col("_segment_start").cast(pl.Utf8) + "_" + pl.col("_next_segment_end").cast(pl.Utf8))
        .alias("_segment_id")
    )

    # For each segment, check if it actually starts with act1 and ends with act2
    # Get the first and last activity of each segment
    segment_check = (
        df.group_by([case_id_key, "_segment_id"])
        .agg([
            pl.col(activity_key).first().alias("_first_act"),
            pl.col(activity_key).last().alias("_last_act"),
            pl.col("_segment_id").first().alias("_segment_id_check")
        ])
        .filter(
            pl.col("_first_act").is_in(act1_list) &
            pl.col("_last_act").is_in(act2_list)
        )
        .select([case_id_key, "_segment_id_check"])
        .rename({"_segment_id_check": "_segment_id"})
    )

    # Keep only segments that pass the check
    df = df.join(segment_check, on=[case_id_key, "_segment_id"], how="inner", maintain_order="left")

    # Assign subcase numbers
    df = df.with_columns(
        pl.col("_segment_id")
        .rank("dense")
        .over(case_id_key)
        .alias("_subcase_num")
    )

    # Update case ID with subcase information
    df = df.with_columns(
        pl.concat_str([
            pl.col(case_id_key).cast(pl.Utf8),
            pl.lit(subcase_concat_str),
            pl.col("_subcase_num").cast(pl.Utf8)
        ]).alias(case_id_key)
    )

    # Drop helper columns
    df = df.drop([
        "_event_idx", "_is_act1", "_is_act2", "_act1_pos", "_act2_pos",
        "_current_act1", "_segment_start", "_segment_end", "_next_segment_end",
        "_segment_id", "_subcase_num"
    ])

    return df
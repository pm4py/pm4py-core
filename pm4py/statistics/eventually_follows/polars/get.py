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
import polars as pl
from pm4py.util import exec_utils, constants, xes_constants
from pm4py.util.business_hours import soj_time_business_hours_diff
from typing import Optional, Dict, Any, Union, Tuple


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    KEEP_FIRST_FOLLOWING = "keep_first_following"


def get_partial_order_dataframe(
    lf: pl.LazyFrame,
    start_timestamp_key=None,
    timestamp_key="time:timestamp",
    case_id_glue="case:concept:name",
    activity_key="concept:name",
    keep_first_following=True,
    business_hours=False,
    business_hours_slot=None,
    workcalendar=constants.DEFAULT_BUSINESS_HOURS_WORKCALENDAR,
) -> pl.LazyFrame:
    """
    Gets the partial order between events (of the same case) in a Polars LazyFrame

    Parameters
    --------------
    lf
        LazyFrame
    start_timestamp_key
        Start timestamp key (if not provided, defaulted to the timestamp_key)
    timestamp_key
        Complete timestamp
    case_id_glue
        Column of the dataframe to use as case ID
    activity_key
        Activity key
    keep_first_following
        Keep only the first event following the given event
    business_hours
        Whether to compute business hours
    business_hours_slot
        Business hours slot configuration
    workcalendar
        Work calendar configuration

    Returns
    ---------------
    part_ord_dataframe
        Partial order LazyFrame (with flow time between events)
    """
    # if not differently specified, set the start timestamp key to the timestamp key
    if start_timestamp_key is None:
        start_timestamp_key = xes_constants.DEFAULT_START_TIMESTAMP_KEY
        lf = lf.with_columns(pl.col(timestamp_key).alias(start_timestamp_key))

    # Reduce to needed columns for efficiency
    needed_columns = [case_id_glue, activity_key, start_timestamp_key, timestamp_key]
    lf = lf.select(needed_columns)

    # Sort by case ID and timestamps
    lf = lf.sort([case_id_glue, start_timestamp_key, timestamp_key], maintain_order=True)

    # Add index for ordering within cases
    lf = lf.with_row_index("__index__")

    # Self-join to get all pairs within same cases
    lf_self = lf.select([
        pl.col(case_id_glue).alias(case_id_glue + "_2"),
        pl.col(activity_key).alias(activity_key + "_2"),
        pl.col(start_timestamp_key).alias(start_timestamp_key + "_2"),
        pl.col(timestamp_key).alias(timestamp_key + "_2"),
        pl.col("__index__").alias("__index___2")
    ])

    # Join on case ID
    partial_order_df = lf.join(
        lf_self, 
        left_on=case_id_glue, 
        right_on=case_id_glue + "_2",
        how="inner",
        maintain_order="left",
    )

    # Filter to ensure proper ordering and temporal relationships
    partial_order_df = partial_order_df.filter(
        (pl.col("__index__") < pl.col("__index___2")) &
        (pl.col(timestamp_key) <= pl.col(start_timestamp_key + "_2"))
    )

    # Calculate flow time
    if business_hours and business_hours_slot is not None:
        # For business hours, we need to collect and apply Python function
        # This is less efficient but required for business hours calculation
        df_collected = partial_order_df.collect()
        flow_times = []
        for row in df_collected.iter_rows():
            ts_idx = df_collected.columns.index(timestamp_key)
            start_ts_2_idx = df_collected.columns.index(start_timestamp_key + "_2")
            flow_time = soj_time_business_hours_diff(
                row[ts_idx], row[start_ts_2_idx], business_hours_slot, workcalendar
            )
            flow_times.append(flow_time)

        df_collected = df_collected.with_columns(
            pl.Series(constants.DEFAULT_FLOW_TIME, flow_times)
        )
        partial_order_df = df_collected.lazy()
    else:
        # Standard time difference calculation
        partial_order_df = partial_order_df.with_columns(
            (pl.col(start_timestamp_key + "_2") - pl.col(timestamp_key))
            .dt.total_seconds()
            .alias(constants.DEFAULT_FLOW_TIME)
        )

    # Keep only first following if specified
    if keep_first_following:
        partial_order_df = (
            partial_order_df.sort(["__index__", "__index___2"])
            .group_by("__index__", maintain_order=True)
            .first()
        )

    return partial_order_df


def apply(
    lf: pl.LazyFrame,
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> Dict[Tuple[str, str], int]:
    """
    Computes the eventually-follows relationships between activities

    Parameters
    --------------
    lf
        Polars LazyFrame
    parameters
        Parameters of the algorithm

    Returns
    --------------
    ret_dict
        Dictionary with eventually-follows relationships and their counts
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(
        Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY
    )
    case_id_glue = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME
    )
    timestamp_key = exec_utils.get_param_value(
        Parameters.TIMESTAMP_KEY,
        parameters,
        xes_constants.DEFAULT_TIMESTAMP_KEY,
    )
    start_timestamp_key = exec_utils.get_param_value(
        Parameters.START_TIMESTAMP_KEY, parameters, None
    )
    keep_first_following = exec_utils.get_param_value(
        Parameters.KEEP_FIRST_FOLLOWING, parameters, False
    )

    partial_order_dataframe = get_partial_order_dataframe(
        lf,
        start_timestamp_key=start_timestamp_key,
        timestamp_key=timestamp_key,
        case_id_glue=case_id_glue,
        activity_key=activity_key,
        keep_first_following=keep_first_following,
    )

    # Group by activity pairs and count
    ret_dict_df = partial_order_dataframe.group_by([activity_key, activity_key + "_2"]).len(name="count").collect()

    ret_dict = {}
    for row in ret_dict_df.iter_rows():
        key = (row[0], row[1])
        count = row[2]
        ret_dict[key] = int(count)

    return ret_dict

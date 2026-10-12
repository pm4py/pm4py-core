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
from typing import Optional, Dict, Any, Union, Tuple


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    STRICT = "strict"


def get_concurrent_events_dataframe(
    lf: pl.LazyFrame,
    start_timestamp_key=None,
    timestamp_key="time:timestamp",
    case_id_glue="case:concept:name",
    activity_key="concept:name",
    strict=False,
) -> pl.LazyFrame:
    """
    Gets the concurrent events (of the same case) in a Polars LazyFrame

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
    strict
        Gets only entries that are strictly concurrent (i.e. the length of the intersection as real interval is > 0)

    Returns
    ---------------
    conc_ev_dataframe
        Concurrent events LazyFrame with concurrency information
    """
    # if not differently specified, set the start timestamp key to the timestamp key
    if start_timestamp_key is None:
        start_timestamp_key = xes_constants.DEFAULT_START_TIMESTAMP_KEY
        lf = lf.with_columns(pl.col(timestamp_key).alias(start_timestamp_key))

    # Sort by case ID and timestamps
    lf = lf.sort([case_id_glue, start_timestamp_key, timestamp_key], maintain_order=True)

    # Reduce to needed columns for efficiency
    lf = lf.select([case_id_glue, activity_key, start_timestamp_key, timestamp_key])

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
    concurrent_df = lf.join(
        lf_self, 
        left_on=case_id_glue, 
        right_on=case_id_glue + "_2",
        how="inner",
        maintain_order="left",
    )

    # Filter to avoid duplicates - only keep pairs where first index < second index
    concurrent_df = concurrent_df.filter(
        pl.col("__index__") < pl.col("__index___2")
    )

    # Calculate overlap of time intervals
    max_start_col = "__max_start_column"
    min_complete_col = "__min_complete_column"
    diff_col = "__diff_maxs_minc"

    concurrent_df = concurrent_df.with_columns([
        pl.max_horizontal([pl.col(start_timestamp_key), pl.col(start_timestamp_key + "_2")]).alias(max_start_col),
        pl.min_horizontal([pl.col(timestamp_key), pl.col(timestamp_key + "_2")]).alias(min_complete_col)
    ])

    # Calculate time difference (in seconds)
    concurrent_df = concurrent_df.with_columns(
        (pl.col(min_complete_col) - pl.col(max_start_col)).dt.total_seconds().alias(diff_col)
    )

    # Filter based on strict parameter
    if strict:
        concurrent_df = concurrent_df.filter(pl.col(diff_col) > 0)
    else:
        concurrent_df = concurrent_df.filter(pl.col(diff_col) >= 0)

    return concurrent_df


def apply(
    lf: pl.LazyFrame,
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> Dict[Tuple[str, str], int]:
    """
    Gets the number of times for which two activities have been concurrent
    in the log.

    Parameters
    ----------
    lf
        Polars LazyFrame
    parameters
        Parameters of the algorithm, including:

        - Parameters.ACTIVITY_KEY => activity key
        - Parameters.CASE_ID_KEY => case id
        - Parameters.START_TIMESTAMP_KEY => start timestamp
        - Parameters.TIMESTAMP_KEY => complete timestamp
        - Parameters.STRICT => Determine if only entries that are strictly concurrent (i.e. the length of the intersection as real interval is > 0) should be obtained. Default: False

    Returns
    --------------
    ret_dict
        Dictionaries associating to a couple of activities (tuple) the number of times for which they have been
        executed in parallel in the log

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
    strict = exec_utils.get_param_value(Parameters.STRICT, parameters, False)

    concurrent_dataframe = get_concurrent_events_dataframe(
        lf,
        start_timestamp_key=start_timestamp_key,
        timestamp_key=timestamp_key,
        case_id_glue=case_id_glue,
        activity_key=activity_key,
        strict=strict,
    )

    # Group by activity pairs and count
    ret_dict0_df = concurrent_dataframe.group_by([activity_key, activity_key + "_2"]).len(name="count").collect()

    ret_dict0 = {}
    for row in ret_dict0_df.iter_rows():
        key = (row[0], row[1])
        count = row[2]
        ret_dict0[key] = count

    ret_dict = {}

    # Ensure we avoid problems with duplicates by using sorted tuples
    for el in ret_dict0:
        # avoid getting two entries for the same set of concurrent activities
        el2 = tuple(sorted(el))
        if el2 in ret_dict:
            ret_dict[el2] += int(ret_dict0[el])
        else:
            ret_dict[el2] = int(ret_dict0[el])

    return ret_dict
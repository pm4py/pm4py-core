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
from pm4py.util.xes_constants import DEFAULT_NAME_KEY
from pm4py.util.xes_constants import DEFAULT_TIMESTAMP_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ATTRIBUTE_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_CASEID_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_TIMESTAMP_KEY
from pm4py.util.constants import DEFAULT_VARIANT_SEP
from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any, Union, Tuple, List
import polars as pl
import sys


class Parameters(Enum):
    CASE_ID_KEY = PARAMETER_CONSTANT_CASEID_KEY
    ATTRIBUTE_KEY = PARAMETER_CONSTANT_ATTRIBUTE_KEY
    TIMESTAMP_KEY = PARAMETER_CONSTANT_TIMESTAMP_KEY
    TARGET_ATTRIBUTE_KEY = "target_attribute_key"
    DECREASING_FACTOR = "decreasingFactor"
    POSITIVE = "positive"
    MIN_PERFORMANCE = "min_performance"
    MAX_PERFORMANCE = "max_performance"


def apply(
    df: pl.LazyFrame,
    paths: List[Tuple[str, str]],
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> pl.LazyFrame:
    """
    Apply a filter on traces containing / not containing a path

    Parameters
    ----------
    df
        LazyFrame
    paths
        Paths to filter on
    parameters
        Possible parameters of the algorithm, including:
            Parameters.CASE_ID_KEY -> Case ID column in the LazyFrame
            Parameters.ATTRIBUTE_KEY -> Attribute we want to filter
            Parameters.POSITIVE -> Specifies if the filter should be applied including traces (positive=True)
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
    attribute_key = exec_utils.get_param_value(
        Parameters.ATTRIBUTE_KEY, parameters, DEFAULT_NAME_KEY
    )
    timestamp_key = exec_utils.get_param_value(
        Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY
    )
    target_attribute_key = exec_utils.get_param_value(
        Parameters.TARGET_ATTRIBUTE_KEY, parameters, attribute_key
    )
    positive = exec_utils.get_param_value(
        Parameters.POSITIVE, parameters, True
    )

    # Convert paths to string format
    paths_str = [path[0] + DEFAULT_VARIANT_SEP + path[1] for path in paths]

    # Sort by case and timestamp
    df = df.sort([case_id_glue, timestamp_key], maintain_order=True)

    # Get next activity using shift
    df = df.with_columns([
        pl.col(case_id_glue).alias("case_next"),
        pl.col(target_attribute_key).shift(-1).over(case_id_glue).alias("next_activity")
    ])

    # Create path column
    df = df.with_columns(
        pl.when(pl.col("case_next") == pl.col(case_id_glue))
        .then(
            pl.concat_str([
                pl.col(attribute_key),
                pl.lit(DEFAULT_VARIANT_SEP),
                pl.col("next_activity")
            ])
        )
        .otherwise(None)
        .alias("@@path")
    )

    # Get cases with matching paths
    matching_cases = (
        df.filter(pl.col("@@path").is_in(paths_str))
        .select(case_id_glue)
        .unique()
    )

    # Apply positive/negative filter
    if positive:
        ret = df.join(matching_cases, on=case_id_glue, how="inner", maintain_order="left")
    else:
        ret = df.join(matching_cases, on=case_id_glue, how="anti", maintain_order="left")

    # Clean up helper columns
    ret = ret.drop(["case_next", "next_activity", "@@path"])

    return ret


def apply_performance(
    df: pl.LazyFrame,
    provided_path: Tuple[str, str],
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> pl.LazyFrame:
    """
    Filters the cases of a LazyFrame where there is at least one occurrence of the provided path
    occurring in the defined timedelta range.

    Parameters
    ----------
    df
        LazyFrame
    provided_path
        Path to filter on
    parameters
        Possible parameters of the algorithm, including:
            Parameters.CASE_ID_KEY -> Case ID column in the LazyFrame
            Parameters.ATTRIBUTE_KEY -> Attribute we want to filter
            Parameters.TIMESTAMP_KEY -> Attribute identifying the timestamp in the log
            Parameters.POSITIVE -> Specifies if the filter should be applied including traces (positive=True)
            or excluding traces (positive=False)
            Parameters.MIN_PERFORMANCE -> Minimal allowed performance of the provided path
            Parameters.MAX_PERFORMANCE -> Maximal allowed performance of the provided path

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
    attribute_key = exec_utils.get_param_value(
        Parameters.ATTRIBUTE_KEY, parameters, DEFAULT_NAME_KEY
    )
    timestamp_key = exec_utils.get_param_value(
        Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY
    )
    positive = exec_utils.get_param_value(
        Parameters.POSITIVE, parameters, True
    )
    provided_path_str = provided_path[0] + DEFAULT_VARIANT_SEP + provided_path[1]
    min_performance = exec_utils.get_param_value(
        Parameters.MIN_PERFORMANCE, parameters, 0
    )
    max_performance = exec_utils.get_param_value(
        Parameters.MAX_PERFORMANCE, parameters, sys.maxsize
    )

    # Sort by case and timestamp
    df = df.sort([case_id_glue, timestamp_key], maintain_order=True)

    # Get next activity and timestamp using shift
    df = df.with_columns([
        pl.col(case_id_glue).alias("case_next"),
        pl.col(attribute_key).shift(-1).over(case_id_glue).alias("next_activity"),
        pl.col(timestamp_key).shift(-1).over(case_id_glue).alias("next_timestamp")
    ])

    # Create path column and calculate duration
    df = df.with_columns([
        pl.when(pl.col("case_next") == pl.col(case_id_glue))
        .then(
            pl.concat_str([
                pl.col(attribute_key),
                pl.lit(DEFAULT_VARIANT_SEP),
                pl.col("next_activity")
            ])
        )
        .otherwise(None)
        .alias("@@path"),
        pl.when(pl.col("case_next") == pl.col(case_id_glue))
        .then(
            (pl.col("next_timestamp") - pl.col(timestamp_key)).dt.total_seconds()
        )
        .otherwise(None)
        .alias("@@duration")
    ])

    # Get cases with matching paths within performance bounds
    matching_cases = (
        df.filter(
            (pl.col("@@path") == provided_path_str) &
            (pl.col("@@duration") >= min_performance) &
            (pl.col("@@duration") <= max_performance)
        )
        .select(case_id_glue)
        .unique()
    )

    # Apply positive/negative filter
    if positive:
        ret = df.join(matching_cases, on=case_id_glue, how="inner", maintain_order="left")
    else:
        ret = df.join(matching_cases, on=case_id_glue, how="anti", maintain_order="left")

    # Clean up helper columns
    ret = ret.drop(["case_next", "next_activity", "next_timestamp", "@@path", "@@duration"])

    return ret
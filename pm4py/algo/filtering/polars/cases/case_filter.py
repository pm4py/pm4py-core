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
from pm4py.util import constants, xes_constants
from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any, Union
import polars as pl
from datetime import timedelta


class Parameters(Enum):
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY

    BUSINESS_HOURS = "business_hours"
    BUSINESS_HOUR_SLOTS = "business_hour_slots"
    WORKCALENDAR = "workcalendar"


def filter_on_ncases(
    df: pl.LazyFrame,
    case_id_glue: str = constants.CASE_CONCEPT_NAME,
    max_no_cases: int = 1000,
) -> pl.LazyFrame:
    """
    Filter a LazyFrame keeping only the specified maximum number of traces

    Parameters
    -----------
    df
        LazyFrame
    case_id_glue
        Case ID column
    max_no_cases
        Maximum number of traces to keep

    Returns
    ------------
    df
        Filtered LazyFrame
    """
    # Get case counts and select top cases
    cases_to_keep = (
        df.group_by(case_id_glue, maintain_order=True)
        .len(name="count")
        .sort("count", descending=True, maintain_order=True)
        .limit(max_no_cases)
        .select(case_id_glue)
    )

    # Keep only events from selected cases
    ret = df.join(cases_to_keep, on=case_id_glue, how="inner", maintain_order="left")

    return ret


def filter_on_case_size(
    df: pl.LazyFrame,
    case_id_glue: str = "case:concept:name",
    min_case_size: int = 2,
    max_case_size: Optional[int] = None,
) -> pl.LazyFrame:
    """
    Filter a LazyFrame keeping only traces with at least the specified number of events

    Parameters
    -----------
    df
        LazyFrame
    case_id_glue
        Case ID column
    min_case_size
        Minimum size of a case
    max_case_size
        Maximum case size

    Returns
    -----------
    df
        Filtered LazyFrame
    """
    # Count events per case
    case_sizes = (
        df.group_by(case_id_glue)
        .len(name="count")
        .filter(pl.col("count") >= min_case_size)
    )

    if max_case_size is not None:
        case_sizes = case_sizes.filter(pl.col("count") <= max_case_size)

    # Keep only cases that meet size criteria
    ret = df.join(case_sizes.select(case_id_glue), on=case_id_glue, how="inner", maintain_order="left")

    return ret


def filter_on_case_performance(
    df: pl.LazyFrame,
    case_id_glue: str = constants.CASE_CONCEPT_NAME,
    timestamp_key: str = xes_constants.DEFAULT_TIMESTAMP_KEY,
    min_case_performance: float = 0,
    max_case_performance: float = 10000000000,
    business_hours: bool = False,
    business_hours_slots=None,
) -> pl.LazyFrame:
    """
    Filter a LazyFrame on case performance

    Parameters
    -----------
    df
        LazyFrame
    case_id_glue
        Case ID column
    timestamp_key
        Timestamp column to use
    min_case_performance
        Minimum case performance (in seconds)
    max_case_performance
        Maximum case performance (in seconds)
    business_hours
        Whether to calculate duration using business hours
    business_hours_slots
        Business hour slots (if business_hours is True)

    Returns
    -----------
    df
        Filtered LazyFrame
    """
    if business_hours:
        # Business hours calculation not implemented in this version
        raise NotImplementedError("Business hours calculation is not yet implemented for Polars filtering")

    # Calculate case durations
    case_durations = (
        df.group_by(case_id_glue)
        .agg([
            pl.col(timestamp_key).min().alias("start_time"),
            pl.col(timestamp_key).max().alias("end_time")
        ])
        .with_columns(
            ((pl.col("end_time") - pl.col("start_time")).dt.total_seconds()).alias("case_duration")
        )
        .filter(
            (pl.col("case_duration") >= min_case_performance) &
            (pl.col("case_duration") <= max_case_performance)
        )
        .select(case_id_glue)
    )

    # Keep only cases that meet performance criteria
    ret = df.join(case_durations, on=case_id_glue, how="inner", maintain_order="left")

    return ret


def filter_case_performance(
    df: pl.LazyFrame,
    min_case_performance: float = 0,
    max_case_performance: float = 10000000000,
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> pl.LazyFrame:
    """
    Filter a LazyFrame on case performance using parameters

    Parameters
    -----------
    df
        LazyFrame
    min_case_performance
        Minimum case performance (in seconds)
    max_case_performance
        Maximum case performance (in seconds)
    parameters
        Parameters dictionary

    Returns
    -----------
    df
        Filtered LazyFrame
    """
    if parameters is None:
        parameters = {}

    timestamp_key = exec_utils.get_param_value(
        Parameters.TIMESTAMP_KEY,
        parameters,
        xes_constants.DEFAULT_TIMESTAMP_KEY,
    )
    case_glue = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME
    )
    business_hours = exec_utils.get_param_value(
        Parameters.BUSINESS_HOURS, parameters, False
    )
    business_hours_slots = exec_utils.get_param_value(
        Parameters.BUSINESS_HOUR_SLOTS,
        parameters,
        constants.DEFAULT_BUSINESS_HOUR_SLOTS,
    )

    return filter_on_case_performance(
        df,
        min_case_performance=min_case_performance,
        max_case_performance=max_case_performance,
        timestamp_key=timestamp_key,
        case_id_glue=case_glue,
        business_hours=business_hours,
        business_hours_slots=business_hours_slots,
    )


def apply(df, parameters=None):
    del df
    del parameters
    raise NotImplementedError("apply method not available for case filter")


def apply_auto_filter(df, parameters=None):
    del df
    del parameters
    raise Exception("apply_auto_filter method not available for case filter")

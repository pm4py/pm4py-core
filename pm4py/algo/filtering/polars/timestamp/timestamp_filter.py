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
from pm4py.util.constants import CASE_CONCEPT_NAME, PARAMETER_CONSTANT_CASEID_KEY, PARAMETER_CONSTANT_TIMESTAMP_KEY
from pm4py.algo.filtering.common.timestamp.timestamp_common import get_dt_from_string
from pm4py.util.xes_constants import DEFAULT_TIMESTAMP_KEY
from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any, Union
import polars as pl
import datetime


class Parameters(Enum):
    TIMESTAMP_KEY = PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = PARAMETER_CONSTANT_CASEID_KEY


def filter_traces_contained(
    df: pl.LazyFrame,
    dt1: Union[str, datetime.datetime],
    dt2: Union[str, datetime.datetime],
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> pl.LazyFrame:
    """
    Get traces that are contained in the given interval

    Parameters
    ----------
    df
        Polars LazyFrame
    dt1
        Lower bound to the interval (possibly expressed as string, but automatically converted)
    dt2
        Upper bound to the interval (possibly expressed as string, but automatically converted)
    parameters
        Possible parameters of the algorithm, including:
            Parameters.TIMESTAMP_KEY -> Attribute to use as timestamp
            Parameters.CASE_ID_KEY -> Column that contains the case ID

    Returns
    ----------
    df
        Filtered LazyFrame
    """
    if parameters is None:
        parameters = {}
    timestamp_key = exec_utils.get_param_value(
        Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY
    )
    case_id_glue = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME
    )
    dt1 = get_dt_from_string(dt1)
    dt2 = get_dt_from_string(dt2)

    # Group by case and get first and last timestamp
    case_boundaries = (
        df.group_by(case_id_glue)
        .agg([
            pl.col(timestamp_key).min().alias("first_timestamp"),
            pl.col(timestamp_key).max().alias("last_timestamp")
        ])
    )

    # Filter cases where both first and last timestamp are within bounds
    valid_cases = case_boundaries.filter(
        (pl.col("first_timestamp") >= dt1) &
        (pl.col("last_timestamp") <= dt2)
    ).select(case_id_glue)

    # Keep only events from valid cases
    ret = df.join(valid_cases, on=case_id_glue, how="inner", maintain_order="left")

    return ret


def filter_traces_intersecting(
    df: pl.LazyFrame,
    dt1: Union[str, datetime.datetime],
    dt2: Union[str, datetime.datetime],
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> pl.LazyFrame:
    """
    Filter traces intersecting the given interval

    Parameters
    ----------
    df
        Polars LazyFrame
    dt1
        Lower bound to the interval (possibly expressed as string, but automatically converted)
    dt2
        Upper bound to the interval (possibly expressed as string, but automatically converted)
    parameters
        Possible parameters of the algorithm, including:
            Parameters.TIMESTAMP_KEY -> Attribute to use as timestamp
            Parameters.CASE_ID_KEY -> Column that contains the case ID

    Returns
    ----------
    df
        Filtered LazyFrame
    """
    if parameters is None:
        parameters = {}
    timestamp_key = exec_utils.get_param_value(
        Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY
    )
    case_id_glue = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME
    )
    dt1 = get_dt_from_string(dt1)
    dt2 = get_dt_from_string(dt2)

    # Group by case and get first and last timestamp
    case_boundaries = (
        df.group_by(case_id_glue)
        .agg([
            pl.col(timestamp_key).min().alias("first_timestamp"),
            pl.col(timestamp_key).max().alias("last_timestamp")
        ])
    )

    # A trace intersects if:
    # 1. It has an event within the interval (first > dt1 and first < dt2) OR
    # 2. It has an event within the interval (last > dt1 and last < dt2) OR
    # 3. It spans the entire interval (first < dt1 and last > dt2)
    valid_cases = case_boundaries.filter(
        ((pl.col("first_timestamp") > dt1) & (pl.col("first_timestamp") < dt2)) |
        ((pl.col("last_timestamp") > dt1) & (pl.col("last_timestamp") < dt2)) |
        ((pl.col("first_timestamp") < dt1) & (pl.col("last_timestamp") > dt2))
    ).select(case_id_glue)

    # Keep only events from valid cases
    ret = df.join(valid_cases, on=case_id_glue, how="inner", maintain_order="left")

    return ret


def apply_events(
    df: pl.LazyFrame,
    dt1: Union[str, datetime.datetime],
    dt2: Union[str, datetime.datetime],
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> pl.LazyFrame:
    """
    Get a new log containing all the events contained in the given interval

    Parameters
    ----------
    df
        Polars LazyFrame
    dt1
        Lower bound to the interval (possibly expressed as string, but automatically converted)
    dt2
        Upper bound to the interval (possibly expressed as string, but automatically converted)
    parameters
        Possible parameters of the algorithm, including:
            Parameters.TIMESTAMP_KEY -> Attribute to use as timestamp

    Returns
    ----------
    df
        Filtered LazyFrame
    """
    if parameters is None:
        parameters = {}

    timestamp_key = exec_utils.get_param_value(
        Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY
    )
    dt1 = get_dt_from_string(dt1)
    dt2 = get_dt_from_string(dt2)

    # Filter events directly
    ret = df.filter(
        (pl.col(timestamp_key) >= dt1) &
        (pl.col(timestamp_key) <= dt2)
    )

    return ret


def filter_traces_attribute_in_timeframe(
    df: pl.LazyFrame,
    attribute: str,
    attribute_value: str,
    dt1: Union[str, datetime.datetime],
    dt2: Union[str, datetime.datetime],
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> pl.LazyFrame:
    """
    Get a new log containing all the traces that have an event in the given interval with the specified attribute value

    Parameters
    -----------
    df
        LazyFrame
    attribute
        The attribute to filter on
    attribute_value
        The attribute value to filter on
    dt1
        Lower bound to the interval
    dt2
        Upper bound to the interval
    parameters
        Possible parameters of the algorithm, including:
            Parameters.TIMESTAMP_KEY -> Attribute to use as timestamp
            Parameters.CASE_ID_KEY -> Column that contains the case ID

    Returns
    ------------
    df
        Filtered LazyFrame
    """
    if parameters is None:
        parameters = {}
    timestamp_key = exec_utils.get_param_value(
        Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY
    )
    case_id_glue = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME
    )

    dt1 = get_dt_from_string(dt1)
    dt2 = get_dt_from_string(dt2)

    # Find cases that have the attribute value in the timeframe
    valid_cases = (
        df.filter(
            (pl.col(attribute) == attribute_value) &
            (pl.col(timestamp_key) >= dt1) &
            (pl.col(timestamp_key) <= dt2)
        )
        .select(case_id_glue)
        .unique()
    )

    # Keep all events from those cases
    filtered = df.join(valid_cases, on=case_id_glue, how="inner", maintain_order="left")

    return filtered


def apply(df, parameters=None):
    del df
    del parameters
    raise Exception("apply method not available for timestamp filter")


def apply_auto_filter(df, parameters=None):
    del df
    del parameters
    raise Exception(
        "apply_auto_filter method not available for timestamp filter"
    )
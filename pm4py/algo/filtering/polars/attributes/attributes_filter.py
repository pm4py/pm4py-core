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
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ATTRIBUTE_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_CASEID_KEY
from enum import Enum
from pm4py.util import exec_utils
from copy import copy
from numbers import Real
from typing import Optional, Dict, Any, Union, List
import polars as pl


class Parameters(Enum):
    ATTRIBUTE_KEY = PARAMETER_CONSTANT_ATTRIBUTE_KEY
    ACTIVITY_KEY = PARAMETER_CONSTANT_ACTIVITY_KEY
    CASE_ID_KEY = PARAMETER_CONSTANT_CASEID_KEY
    DECREASING_FACTOR = "decreasingFactor"
    POSITIVE = "positive"
    STREAM_FILTER_KEY1 = "stream_filter_key1"
    STREAM_FILTER_VALUE1 = "stream_filter_value1"
    STREAM_FILTER_KEY2 = "stream_filter_key2"
    STREAM_FILTER_VALUE2 = "stream_filter_value2"
    KEEP_ONCE_PER_CASE = "keep_once_per_case"


def _attribute_is_in(df: pl.LazyFrame, attribute_key: str, values) -> pl.Expr:
    """Compare numeric values without the implicit casts removed in Polars 2.0."""
    values = list(values)
    dtype = df.collect_schema()[attribute_key]
    expr = pl.col(attribute_key)
    if all(value is None or isinstance(value, Real) for value in values):
        if dtype.is_float():
            # Widen Float32 too, so a fractional needle is never rounded to a match.
            expr = expr.cast(pl.Float64)
            needles = pl.Series(values, dtype=pl.Float64, strict=False)
            return expr.is_in(pl.lit(needles).implode())
        if dtype.is_integer():
            # Fractions cannot match integers; avoid truncating them or rounding
            # large integer identifiers through Float64.
            values = [
                int(value)
                for value in values
                if value is not None and value % 1 == 0
            ]
            needles = pl.Series(values, dtype=pl.Int128).cast(dtype, strict=False)
            return expr.is_in(pl.lit(needles).implode())
    return expr.is_in(values)


def get_attribute_values(
    df: pl.LazyFrame,
    attribute_key: str,
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> Dict[Any, int]:
    """
    Return list of attribute values contained in the specified column

    Parameters
    -----------
    df
        Polars LazyFrame
    attribute_key
        Attribute for which we want to known the values and the count
    parameters
        Possible parameters of the algorithm

    Returns
    -----------
    attributes_values_dict
        Attributes in the specified column, along with their count
    """
    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME
    )
    keep_once_per_case = exec_utils.get_param_value(
        Parameters.KEEP_ONCE_PER_CASE, parameters, False
    )

    if keep_once_per_case:
        # Get unique values per case
        result = (
            df.select(list(dict.fromkeys([case_id_glue, attribute_key])))
            .unique()
            .group_by(attribute_key)
            .len(name="count")
            .collect()
        )
    else:
        # Count all occurrences
        result = (
            df.group_by(attribute_key)
            .len(name="count")
            .collect()
        )

    # Convert to dictionary
    attributes_values_dict = {}
    for row in result.iter_rows():
        attributes_values_dict[row[0]] = row[1]

    return attributes_values_dict


def apply_numeric_events(
    df: pl.LazyFrame,
    int1: float,
    int2: float,
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> pl.LazyFrame:
    """
    Apply a filter on events (numerical filter)

    Parameters
    --------------
    df
        LazyFrame
    int1
        Lower bound of the interval
    int2
        Upper bound of the interval
    parameters
        Possible parameters of the algorithm:
            Parameters.ATTRIBUTE_KEY => indicates which attribute to filter
            positive => keep or remove events?

    Returns
    --------------
    filtered_df
        Filtered LazyFrame
    """
    if parameters is None:
        parameters = {}

    attribute_key = exec_utils.get_param_value(
        Parameters.ATTRIBUTE_KEY, parameters, DEFAULT_NAME_KEY
    )
    positive = exec_utils.get_param_value(
        Parameters.POSITIVE, parameters, True
    )

    if positive:
        ret = df.filter(
            (pl.col(attribute_key) >= int1) & (pl.col(attribute_key) <= int2)
        )
    else:
        ret = df.filter(
            (pl.col(attribute_key) < int1) | (pl.col(attribute_key) > int2)
        )

    return ret


def apply_numeric(
    df: pl.LazyFrame,
    int1: float,
    int2: float,
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> pl.LazyFrame:
    """
    Filter LazyFrame on attribute values (filter cases)

    Parameters
    --------------
    df
        LazyFrame
    int1
        Lower bound of the interval
    int2
        Upper bound of the interval
    parameters
        Possible parameters of the algorithm:
            Parameters.ATTRIBUTE_KEY => indicates which attribute to filter
            Parameters.POSITIVE => keep or remove traces with such events?

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
    positive = exec_utils.get_param_value(
        Parameters.POSITIVE, parameters, True
    )

    # stream_filter_key is helpful to filter on cases containing an event with an attribute
    # in the specified value set, but such events shall have an activity in
    # particular.
    stream_filter_key1 = exec_utils.get_param_value(
        Parameters.STREAM_FILTER_KEY1, parameters, None
    )
    stream_filter_value1 = exec_utils.get_param_value(
        Parameters.STREAM_FILTER_VALUE1, parameters, None
    )
    stream_filter_key2 = exec_utils.get_param_value(
        Parameters.STREAM_FILTER_KEY2, parameters, None
    )
    stream_filter_value2 = exec_utils.get_param_value(
        Parameters.STREAM_FILTER_VALUE2, parameters, None
    )

    # Filter events by numeric range
    filtered_df_by_ev = df.filter(
        (pl.col(attribute_key) >= int1) & (pl.col(attribute_key) <= int2)
    )

    if stream_filter_key1 is not None:
        filtered_df_by_ev = filtered_df_by_ev.filter(
            pl.col(stream_filter_key1) == stream_filter_value1
        )
    if stream_filter_key2 is not None:
        filtered_df_by_ev = filtered_df_by_ev.filter(
            pl.col(stream_filter_key2) == stream_filter_value2
        )

    # Get case IDs that match the criteria
    matching_cases = filtered_df_by_ev.select(case_id_glue).unique()

    if positive:
        # Keep cases that match
        ret = df.join(matching_cases, on=case_id_glue, how="inner", maintain_order="left")
    else:
        # Keep cases that don't match
        ret = df.join(matching_cases, on=case_id_glue, how="anti", maintain_order="left")

    return ret


def apply_events(
    df: pl.LazyFrame,
    values: List[str],
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> pl.LazyFrame:
    """
    Filter LazyFrame on attribute values (filter events)

    Parameters
    ----------
    df
        LazyFrame
    values
        Values to filter on
    parameters
        Possible parameters of the algorithm, including:
            Parameters.ATTRIBUTE_KEY -> Attribute we want to filter
            Parameters.POSITIVE -> Specifies if the filter should be applied including traces (positive=True) or
            excluding traces (positive=False)
    Returns
    ----------
    df
        Filtered LazyFrame
    """
    if parameters is None:
        parameters = {}

    attribute_key = exec_utils.get_param_value(
        Parameters.ATTRIBUTE_KEY, parameters, DEFAULT_NAME_KEY
    )
    positive = exec_utils.get_param_value(
        Parameters.POSITIVE, parameters, True
    )

    predicate = _attribute_is_in(df, attribute_key, values)
    if positive:
        ret = df.filter(predicate)
    else:
        ret = df.filter(~predicate)

    return ret


def apply(
    df: pl.LazyFrame,
    values: List[str],
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> pl.LazyFrame:
    """
    Filter LazyFrame on attribute values (filter traces)

    Parameters
    ----------
    df
        LazyFrame
    values
        Values to filter on
    parameters
        Possible parameters of the algorithm, including:
            Parameters.CASE_ID_KEY -> Case ID column in the LazyFrame
            Parameters.ATTRIBUTE_KEY -> Attribute we want to filter
            Parameters.POSITIVE -> Specifies if the filter should be applied including traces (positive=True) or
            excluding traces (positive=False)
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
    positive = exec_utils.get_param_value(
        Parameters.POSITIVE, parameters, True
    )

    return filter_df_on_attribute_values(
        df,
        values,
        case_id_glue=case_id_glue,
        attribute_key=attribute_key,
        positive=positive,
    )


def filter_df_on_attribute_values(
    df: pl.LazyFrame,
    values: List[str],
    case_id_glue: str = "case:concept:name",
    attribute_key: str = "concept:name",
    positive: bool = True,
) -> pl.LazyFrame:
    """
    Filter LazyFrame on attribute values

    Parameters
    ----------
    df
        LazyFrame
    values
        Values to filter on
    case_id_glue
        Case ID column in the LazyFrame
    attribute_key
        Attribute we want to filter
    positive
        Specifies if the filtered should be applied including traces (positive=True) or excluding traces
        (positive=False)

    Returns
    ----------
    df
        Filtered LazyFrame
    """
    if values is None:
        values = []

    # Get events matching the attribute values
    filtered_df_by_ev = df.filter(_attribute_is_in(df, attribute_key, values))

    # Get unique case IDs from filtered events
    matching_cases = filtered_df_by_ev.select(case_id_glue).unique()

    if positive:
        # Keep cases that have matching events
        ret = df.join(matching_cases, on=case_id_glue, how="inner", maintain_order="left")
    else:
        # Keep cases that don't have matching events
        ret = df.join(matching_cases, on=case_id_glue, how="anti", maintain_order="left")

    return ret


def filter_df_keeping_activ_exc_thresh(
    df: pl.LazyFrame,
    thresh: int,
    act_count0: Optional[Dict[str, int]] = None,
    activity_key: str = "concept:name",
    most_common_variant: Optional[List[str]] = None,
) -> pl.LazyFrame:
    """
    Filter a LazyFrame keeping activities exceeding the threshold

    Parameters
    ------------
    df
        Polars LazyFrame
    thresh
        Threshold to use to cut activities
    act_count0
        (If provided) Dictionary that associates each activity with its count
    activity_key
        Column in which the activity is present
    most_common_variant
        (If provided) List of activities in most common variant

    Returns
    ------------
    df
        Filtered LazyFrame
    """
    if most_common_variant is None:
        most_common_variant = []

    if act_count0 is None:
        act_count0 = get_attribute_values(df, activity_key)

    act_count = [
        k
        for k, v in act_count0.items()
        if v >= thresh or k in most_common_variant
    ]

    if len(act_count) < len(act_count0):
        ret = df.filter(pl.col(activity_key).is_in(act_count))
    else:
        ret = df

    return ret


def filter_df_keeping_spno_activities(
    df: pl.LazyFrame,
    activity_key: str = "concept:name",
    max_no_activities: int = 25,
) -> pl.LazyFrame:
    """
    Filter a LazyFrame on the specified number of attributes

    Parameters
    -----------
    df
        LazyFrame
    activity_key
        Activity key in LazyFrame (must be specified if different from concept:name)
    max_no_activities
        Maximum allowed number of attributes

    Returns
    ------------
    df
        Filtered LazyFrame
    """
    # Get activity counts
    activity_counts = (
        df.group_by(activity_key, maintain_order=True)
        .len(name="count")
        .sort("count", descending=True, maintain_order=True)
        .limit(max_no_activities)
        .collect()
    )

    # Extract activity names to keep
    activity_to_keep = activity_counts[activity_key].to_list()

    # Get total unique activities in original dataframe
    total_activities = df.select(pl.col(activity_key).n_unique()).collect()[0, 0]

    if len(activity_to_keep) < total_activities:
        ret = df.filter(pl.col(activity_key).is_in(activity_to_keep))
    else:
        ret = df

    return ret


def filter_df_relative_occurrence_event_attribute(
    df: pl.LazyFrame,
    min_relative_stake: float,
    parameters: Optional[Dict[Any, Any]] = None,
) -> pl.LazyFrame:
    """
    Filters the event log keeping only the events having an attribute value which occurs:
    - in at least the specified (min_relative_stake) percentage of events, when Parameters.KEEP_ONCE_PER_CASE = False
    - in at least the specified (min_relative_stake) percentage of cases, when Parameters.KEEP_ONCE_PER_CASE = True

    Parameters
    -------------------
    df
        Polars LazyFrame
    min_relative_stake
        Minimum percentage of cases (expressed as a number between 0 and 1) in which the attribute should occur.
    parameters
        Parameters of the algorithm, including:
        - Parameters.ATTRIBUTE_KEY => the attribute to use (default: concept:name)
        - Parameters.KEEP_ONCE_PER_CASE => decides the level of the filter to apply
        (if the filter should be applied on the cases, set it to True).

    Returns
    ------------------
    filtered_df
        Filtered Polars LazyFrame
    """
    if parameters is None:
        parameters = {}

    attribute_key = exec_utils.get_param_value(
        PARAMETER_CONSTANT_ATTRIBUTE_KEY, parameters, DEFAULT_NAME_KEY
    )
    case_id_key = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME
    )
    keep_once_per_case = exec_utils.get_param_value(
        Parameters.KEEP_ONCE_PER_CASE, parameters, True
    )

    parameters_cp = copy(parameters)

    activities_occurrences = get_attribute_values(
        df, attribute_key, parameters=parameters_cp
    )

    if keep_once_per_case:
        # filter on cases
        n_cases = df.select(pl.col(case_id_key).n_unique()).collect()[0, 0]
        filtered_attributes = set(
            x
            for x, y in activities_occurrences.items()
            if y >= min_relative_stake * n_cases
        )
    else:
        # filter on events
        n_events = df.select(pl.len()).collect()[0, 0]
        filtered_attributes = set(
            x
            for x, y in activities_occurrences.items()
            if y >= min_relative_stake * n_events
        )

    return apply_events(df, list(filtered_attributes), parameters=parameters)

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
from pm4py.statistics.attributes.common import get as attributes_common
from pm4py.util.xes_constants import DEFAULT_TIMESTAMP_KEY
from pm4py.util import exec_utils
from pm4py.util import constants
from enum import Enum
from collections import Counter
import polars as pl
import sys
from typing import Optional, Dict, Any, Union, Tuple, List


class Parameters(Enum):
    ATTRIBUTE_KEY = constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    MAX_NO_POINTS_SAMPLE = "max_no_of_points_to_sample"
    KEEP_ONCE_PER_CASE = "keep_once_per_case"
    BW_METHOD = "bw_method"


def __add_left_0(stri: str, target_length: int) -> str:
    """
    Adds left 0s to the current string until the target length is reached

    Parameters
    ----------------
    stri
        String
    target_length
        Target length

    Returns
    ----------------
    stri
        Revised string
    """
    while len(stri) < target_length:
        stri = "0" + stri
    return stri


def get_events_distribution(
    lf: pl.LazyFrame,
    distr_type: str = "days_month",
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> Tuple[List[str], List[int]]:
    """
    Gets the distribution of the events in the specified dimension

    Parameters
    ----------------
    lf
        Polars LazyFrame
    distr_type
        Type of distribution:
        - days_month => Gets the distribution of the events among the days of a month (from 1 to 31)
        - months => Gets the distribution of the events among the months (from 1 to 12)
        - years => Gets the distribution of the events among the years of the event log
        - hours => Gets the distribution of the events among the hours of a day (from 0 to 23)
        - days_week => Gets the distribution of the events among the days of a week (from Monday to Sunday)
        - weeks => Distribution of the events among the weeks of a year (from 0 to 52)
    parameters
        Parameters of the algorithm, including:
        - Parameters.TIMESTAMP_KEY

    Returns
    ----------------
    x
        Points (of the X-axis)
    y
        Points (of the Y-axis)
    """
    if parameters is None:
        parameters = {}

    timestamp_key = exec_utils.get_param_value(
        Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY
    )

    values = None
    all_values = None

    if distr_type == "days_month":
        serie = lf.select(pl.col(timestamp_key).dt.day().alias("value")).group_by("value").len(name="count")
        values_df = serie.collect()
        values = Counter(dict(zip(values_df["value"].to_list(), values_df["count"].to_list())))
        all_values = Counter({i: 0 for i in range(1, 32)})
    elif distr_type == "months":
        serie = lf.select(pl.col(timestamp_key).dt.month().alias("value")).group_by("value").len(name="count")
        values_df = serie.collect()
        values = Counter(dict(zip(values_df["value"].to_list(), values_df["count"].to_list())))
        all_values = Counter({i: 0 for i in range(1, 13)})
    elif distr_type == "years":
        serie = lf.select(pl.col(timestamp_key).dt.year().alias("value")).group_by("value").len(name="count")
        values_df = serie.collect()
        values = Counter(dict(zip(values_df["value"].to_list(), values_df["count"].to_list())))
        all_values = Counter(
            {i: 0 for i in range(min(values), max(values) + 1)}
        )
    elif distr_type == "hours":
        serie = lf.select(pl.col(timestamp_key).dt.hour().alias("value")).group_by("value").len(name="count")
        values_df = serie.collect()
        values = Counter(dict(zip(values_df["value"].to_list(), values_df["count"].to_list())))
        all_values = Counter({i: 0 for i in range(0, 24)})
    elif distr_type == "days_week":
        serie = lf.select(pl.col(timestamp_key).dt.weekday().alias("value")).group_by("value").len(name="count")
        values_df = serie.collect()
        # Convert from Monday=1 to Monday=0 format to match pandas
        values_dict = dict(zip(values_df["value"].to_list(), values_df["count"].to_list()))
        values = Counter({k-1: v for k, v in values_dict.items()})
        all_values = Counter({i: 0 for i in range(0, 7)})
    elif distr_type == "weeks":
        serie = lf.select(pl.col(timestamp_key).dt.week().alias("value")).group_by("value").len(name="count")
        values_df = serie.collect()
        values = Counter(dict(zip(values_df["value"].to_list(), values_df["count"].to_list())))
        all_values = Counter({i: 0 for i in range(0, 53)})

    # make sure that all the possible values appear
    for v in all_values:
        if v not in values:
            values[v] = all_values[v]

    values = sorted([(__add_left_0(str(x), 2), y) for x, y in values.items()])

    if distr_type == "days_week":
        mapping = {
            "00": "Monday",
            "01": "Tuesday",
            "02": "Wednesday",
            "03": "Thursday",
            "04": "Friday",
            "05": "Saturday",
            "06": "Sunday",
        }
        values = [(mapping[x[0]], x[1]) for x in values]

    return [x[0] for x in values], [x[1] for x in values]


def get_attribute_values(
    lf: pl.LazyFrame,
    attribute_key: str,
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> Dict[Any, int]:
    """
    Return list of attribute values contained in the specified column of the LazyFrame

    Parameters
    -----------
    lf
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
        Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME
    )
    keep_once_per_case = exec_utils.get_param_value(
        Parameters.KEEP_ONCE_PER_CASE, parameters, False
    )

    if keep_once_per_case:
        processed_lf = lf.select(list(dict.fromkeys([case_id_glue, attribute_key]))).unique()
    else:
        processed_lf = lf

    value_counts = processed_lf.select(pl.col(attribute_key)).group_by(attribute_key).len(name="count").collect()
    attributes_values_dict = dict(zip(value_counts[attribute_key].to_list(), value_counts["count"].to_list()))

    return attributes_values_dict


def get_kde_numeric_attribute(
    lf: pl.LazyFrame,
    attribute: str,
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> Dict[Any, int]:
    """
    Gets the KDE estimation for the distribution of a numeric attribute values

    Parameters
    -------------
    lf
        Polars LazyFrame
    attribute
        Numeric attribute to analyse
    parameters
        Possible parameters of the algorithm, including:
            graph_points -> number of points to include in the graph
            bw_method -> bandwidth method passed to scipy.stats.gaussian_kde


    Returns
    --------------
    x
        X-axis values to represent
    y
        Y-axis values to represent
    """
    if parameters is None:
        parameters = {}

    max_no_of_points_to_sample = exec_utils.get_param_value(
        Parameters.MAX_NO_POINTS_SAMPLE, parameters, sys.maxsize
    )

    red_lf = lf.filter(pl.col(attribute).is_not_null())

    # Get sample if needed
    if max_no_of_points_to_sample < sys.maxsize:
        red_df = red_lf.collect().sample(n=min(max_no_of_points_to_sample, len(red_lf.collect())))
        values = sorted(red_df[attribute].to_list())
    else:
        values = sorted(red_lf.select(pl.col(attribute)).collect()[attribute].to_list())

    return attributes_common.get_kde_numeric_attribute(
        values, parameters=parameters
    )


def get_kde_numeric_attribute_json(lf, attribute, parameters=None):
    """
    Gets the KDE estimation for the distribution of a numeric attribute values
    (expressed as JSON)

    Parameters
    --------------
    lf
        Polars LazyFrame
    attribute
        Numeric attribute to analyse
    parameters
        Possible parameters of the algorithm, including:
            graph_points -> number of points to include in the graph
            bw_method -> bandwidth method passed to scipy.stats.gaussian_kde

    Returns
    --------------
    json
        JSON representing the graph points
    """
    values = lf.filter(pl.col(attribute).is_not_null()).select(pl.col(attribute)).collect()[attribute].to_list()

    return attributes_common.get_kde_numeric_attribute_json(
        values, parameters=parameters
    )


def get_kde_date_attribute(
    lf, attribute=DEFAULT_TIMESTAMP_KEY, parameters=None
):
    """
    Gets the KDE estimation for the distribution of a date attribute values

    Parameters
    -------------
    lf
        Polars LazyFrame
    attribute
        Date attribute to analyse
    parameters
        Possible parameters of the algorithm, including:
            graph_points -> number of points to include in the graph
            bw_method -> bandwidth method passed to scipy.stats.gaussian_kde


    Returns
    --------------
    x
        X-axis values to represent
    y
        Y-axis values to represent
    """
    if parameters is None:
        parameters = {}

    max_no_of_points_to_sample = exec_utils.get_param_value(
        Parameters.MAX_NO_POINTS_SAMPLE, parameters, sys.maxsize
    )

    red_lf = lf.filter(pl.col(attribute).is_not_null())

    # Get sample if needed
    if max_no_of_points_to_sample < sys.maxsize:
        red_df = red_lf.collect().sample(n=min(max_no_of_points_to_sample, len(red_lf.collect())))
        date_values = sorted(red_df[attribute].to_list())
    else:
        date_values = sorted(red_lf.select(pl.col(attribute)).collect()[attribute].to_list())

    return attributes_common.get_kde_date_attribute(
        date_values, parameters=parameters
    )


def get_kde_date_attribute_json(
    lf, attribute=DEFAULT_TIMESTAMP_KEY, parameters=None
):
    """
    Gets the KDE estimation for the distribution of a date attribute values
    (expressed as JSON)

    Parameters
    --------------
    lf
        Polars LazyFrame
    attribute
        Date attribute to analyse
    parameters
        Possible parameters of the algorithm, including:
            graph_points -> number of points to include in the graph
            bw_method -> bandwidth method passed to scipy.stats.gaussian_kde

    Returns
    --------------
    json
        JSON representing the graph points
    """
    values = lf.filter(pl.col(attribute).is_not_null()).select(pl.col(attribute)).collect()[attribute].to_list()

    return attributes_common.get_kde_date_attribute_json(
        values, parameters=parameters
    )

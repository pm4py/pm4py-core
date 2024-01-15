'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
from pm4py.statistics.attributes.common import get as attributes_common
from pm4py.util.xes_constants import DEFAULT_TIMESTAMP_KEY
from pm4py.util import exec_utils
from pm4py.util import constants
from enum import Enum
from collections import Counter
import pandas as pd
from typing import Optional, Dict, Any, Union, Tuple, List


class Parameters(Enum):
    ATTRIBUTE_KEY = constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    MAX_NO_POINTS_SAMPLE = "max_no_of_points_to_sample"
    KEEP_ONCE_PER_CASE = "keep_once_per_case"


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


def get_events_distribution(df: pd.DataFrame, distr_type: str = "days_month", parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Tuple[List[str], List[int]]:
    """
    Gets the distribution of the events in the specified dimension

    Parameters
    ----------------
    df
        Dataframe
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

    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY)

    values = None
    all_values = None
    if distr_type == "days_month":
        serie = df[timestamp_key].dt.day
        values = Counter(serie.value_counts().to_dict())
        all_values = Counter({i: 0 for i in range(1, 32)})
    elif distr_type == "months":
        serie = df[timestamp_key].dt.month
        values = Counter(serie.value_counts().to_dict())
        all_values = Counter({i: 0 for i in range(1, 13)})
    elif distr_type == "years":
        serie = df[timestamp_key].dt.year
        values = Counter(serie.value_counts().to_dict())
        all_values = Counter({i: 0 for i in range(min(values), max(values)+1)})
    elif distr_type == "hours":
        serie = df[timestamp_key].dt.hour
        values = Counter(serie.value_counts().to_dict())
        all_values = Counter({i: 0 for i in range(0, 24)})
    elif distr_type == "days_week":
        serie = df[timestamp_key].dt.dayofweek
        values = Counter(serie.value_counts().to_dict())
        all_values = Counter({i: 0 for i in range(0, 7)})
    elif distr_type == "weeks":
        serie = df[timestamp_key].dt.isocalendar().week
        values = Counter(serie.value_counts().to_dict())
        all_values = Counter({i: 0 for i in range(0, 53)})

    # make sure that all the possible values appear
    for v in all_values:
        if v not in values:
            values[v] = all_values[v]

    values = sorted([(__add_left_0(str(x), 2), y) for x, y in values.items()])

    if distr_type == "days_week":
        mapping = {"00": "Monday", "01": "Tuesday", "02": "Wednesday", "03": "Thursday", "04": "Friday",
                   "05": "Saturday", "06": "Sunday"}
        values = [(mapping[x[0]], x[1]) for x in values]

    return [x[0] for x in values], [x[1] for x in values]


def get_attribute_values(df: pd.DataFrame, attribute_key: str, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Dict[Any, int]:
    """
    Return list of attribute values contained in the specified column of the CSV

    Parameters
    -----------
    df
        Pandas dataframe
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

    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
    keep_once_per_case = exec_utils.get_param_value(Parameters.KEEP_ONCE_PER_CASE, parameters, False)

    if keep_once_per_case:
        df = df.groupby([case_id_glue, attribute_key]).first().reset_index()
    attributes_values_dict = df[attribute_key].value_counts().to_dict()
    # print("attributes_values_dict=",attributes_values_dict)
    return attributes_values_dict


def get_kde_numeric_attribute(df: pd.DataFrame, attribute: str, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Dict[Any, int]:
    """
    Gets the KDE estimation for the distribution of a numeric attribute values

    Parameters
    -------------
    df
        Pandas dataframe
    attribute
        Numeric attribute to analyse
    parameters
        Possible parameters of the algorithm, including:
            graph_points -> number of points to include in the graph


    Returns
    --------------
    x
        X-axis values to represent
    y
        Y-axis values to represent
    """
    if parameters is None:
        parameters = {}

    max_no_of_points_to_sample = exec_utils.get_param_value(Parameters.MAX_NO_POINTS_SAMPLE, parameters, 100000)
    red_df = df.dropna(subset=[attribute])
    if len(red_df) > max_no_of_points_to_sample:
        red_df = red_df.sample(n=max_no_of_points_to_sample)
    values = list(red_df[attribute])

    return attributes_common.get_kde_numeric_attribute(values, parameters=parameters)


def get_kde_numeric_attribute_json(df, attribute, parameters=None):
    """
    Gets the KDE estimation for the distribution of a numeric attribute values
    (expressed as JSON)

    Parameters
    --------------
    df
        Pandas dataframe
    attribute
        Numeric attribute to analyse
    parameters
        Possible parameters of the algorithm, including:
            graph_points -> number of points to include in the graph

    Returns
    --------------
    json
        JSON representing the graph points
    """
    values = list(df.dropna(subset=[attribute])[attribute])

    return attributes_common.get_kde_numeric_attribute_json(values, parameters=parameters)


def get_kde_date_attribute(df, attribute=DEFAULT_TIMESTAMP_KEY, parameters=None):
    """
    Gets the KDE estimation for the distribution of a date attribute values

    Parameters
    -------------
    df
        Pandas dataframe
    attribute
        Date attribute to analyse
    parameters
        Possible parameters of the algorithm, including:
            graph_points -> number of points to include in the graph


    Returns
    --------------
    x
        X-axis values to represent
    y
        Y-axis values to represent
    """
    if parameters is None:
        parameters = {}

    max_no_of_points_to_sample = exec_utils.get_param_value(Parameters.MAX_NO_POINTS_SAMPLE, parameters, 100000)
    red_df = df.dropna(subset=[attribute])
    if len(red_df) > max_no_of_points_to_sample:
        red_df = red_df.sample(n=max_no_of_points_to_sample)
    date_values = list(red_df[attribute])
    return attributes_common.get_kde_date_attribute(date_values, parameters=parameters)


def get_kde_date_attribute_json(df, attribute=DEFAULT_TIMESTAMP_KEY, parameters=None):
    """
    Gets the KDE estimation for the distribution of a date attribute values
    (expressed as JSON)

    Parameters
    --------------
    df
        Pandas dataframe
    attribute
        Date attribute to analyse
    parameters
        Possible parameters of the algorithm, including:
            graph_points -> number of points to include in the graph

    Returns
    --------------
    json
        JSON representing the graph points
    """
    values = list(df.dropna(subset=[attribute])[attribute])

    return attributes_common.get_kde_date_attribute_json(values, parameters=parameters)

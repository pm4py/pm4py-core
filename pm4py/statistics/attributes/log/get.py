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
from pm4py.objects.conversion.log import converter as log_conversion
from pm4py.objects.log.obj import EventLog
from pm4py.util import xes_constants as xes
from pm4py.util.xes_constants import DEFAULT_TIMESTAMP_KEY
from pm4py.util import exec_utils
from pm4py.util import constants
from enum import Enum
from collections import Counter
from copy import copy
from typing import Optional, Dict, Any, Union, Tuple, List, Set
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.util.dt_parsing.variants import strpfromiso


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


def get_events_distribution(log: EventLog, distr_type: str = "days_month", parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Tuple[List[str], List[int]]:
    """
    Gets the distribution of the events in the specified dimension

    Parameters
    ----------------
    log
        Event log
    distr_type
        Type of distribution:
        - days_month => Gets the distribution of the events among the days of a month (from 1 to 31)
        - months => Gets the distribution of the events among the months (from 1 to 12)
        - years => Gets the distribution of the events among the years of the event log
        - hours => Gets the distribution of the events among the hours of a day (from 0 to 23)
        - days_week => Gets the distribution of the events among the days of a week (from Monday to Sunday)
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

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY)

    timestamp_values = []
    for trace in log:
        for event in trace:
            timestamp_values.append(event[timestamp_key])

    values = None
    all_values = None
    if distr_type == "days_month":
        values = Counter(x.day for x in timestamp_values)
        all_values = Counter({i: 0 for i in range(1, 32)})
    elif distr_type == "months":
        values = Counter(x.month for x in timestamp_values)
        all_values = Counter({i: 0 for i in range(1, 13)})
    elif distr_type == "years":
        values = Counter(x.year for x in timestamp_values)
        all_values = Counter({i: 0 for i in range(min(values), max(values)+1)})
    elif distr_type == "hours":
        values = Counter(x.hour for x in timestamp_values)
        all_values = Counter({i: 0 for i in range(0, 24)})
    elif distr_type == "days_week":
        values = Counter(x.weekday() for x in timestamp_values)
        all_values = Counter({i: 0 for i in range(0, 7)})
    elif distr_type == "weeks":
        values = Counter(x.isocalendar().week for x in timestamp_values)
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


def get_all_trace_attributes_from_log(log: EventLog) -> Set[str]:
    """
    Get all trace attributes from the log

    Parameters
    ------------
    log
        Log

    Returns
    ------------
    all_attributes
        All trace attributes from the log
    """
    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG)

    all_attributes = set()
    for trace in log:
        all_attributes = all_attributes.union(set(trace.attributes.keys()))
    if xes.DEFAULT_TRACEID_KEY in all_attributes:
        all_attributes.remove(xes.DEFAULT_TRACEID_KEY)
    return all_attributes


def get_all_event_attributes_from_log(log: EventLog) -> Set[str]:
    """
    Get all events attributes from the log

    Parameters
    -------------
    log
        Log

    Returns
    -------------
    all_attributes
        All trace attributes from the log
    """
    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG)

    all_attributes = set()
    for trace in log:
        for event in trace:
            all_attributes = all_attributes.union(set(event.keys()))
    if xes.DEFAULT_TRANSITION_KEY in all_attributes:
        all_attributes.remove(xes.DEFAULT_TRANSITION_KEY)
    return all_attributes


def get_attribute_values(log: EventLog, attribute_key: str, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Dict[Any, int]:
    """
    Get the attribute values of the log for the specified attribute along with their count

    Parameters
    ----------
    log
        Log
    attribute_key
        Attribute for which we would like to know the values along with their count
    parameters
        Possible parameters of the algorithm

    Returns
    ----------
    attributes
        Dictionary of attributes associated with their count
    """
    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    if parameters is None:
        parameters = {}

    keep_once_per_case = exec_utils.get_param_value(Parameters.KEEP_ONCE_PER_CASE, parameters, False)

    attribute_values = {}

    for trace in log:
        trace_values = [x[attribute_key] for x in trace if attribute_key in x]
        if keep_once_per_case:
            trace_values = set(trace_values)

        for val in trace_values:
            if val not in attribute_values:
                attribute_values[val] = 0
            attribute_values[val] = attribute_values[val] + 1

    return attribute_values


def get_trace_attribute_values(log: EventLog, attribute_key: str, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Dict[Any, int]:
    """
    Get the attribute values of the log for the specified attribute along with their count

    Parameters
    ------------
    log
        Log
    attribute_key
        Attribute for which we wish to get the values along with their count
    parameters
        Possible parameters of the algorithm

    Returns
    ------------
    attributes
        Dictionary of attributes associated with their count
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    attributes = {}

    for trace in log:
        if attribute_key in trace.attributes:
            attribute = trace.attributes[attribute_key]
            if attribute not in attributes:
                attributes[attribute] = 0
            attributes[attribute] = attributes[attribute] + 1

    return attributes


def get_kde_numeric_attribute(log, attribute, parameters=None):
    """
    Gets the KDE estimation for the distribution of a numeric attribute values

    Parameters
    -------------
    log
        Event stream object (if log, is converted)
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

    this_parameters = copy(parameters)
    this_parameters["deepcopy"] = False
    this_parameters["include_case_attributes"] = False

    event_log = log_conversion.apply(log, variant=log_conversion.TO_EVENT_STREAM, parameters=this_parameters)

    values = [event[attribute] for event in event_log if attribute in event]

    return attributes_common.get_kde_numeric_attribute(values, parameters=parameters)


def get_kde_numeric_attribute_json(log, attribute, parameters=None):
    """
    Gets the KDE estimation for the distribution of a numeric attribute values
    (expressed as JSON)

    Parameters
    -------------
    log
        Event log object (if log, is converted)
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

    this_parameters = copy(parameters)
    this_parameters["deepcopy"] = False
    this_parameters["include_case_attributes"] = False

    event_log = log_conversion.apply(log, variant=log_conversion.TO_EVENT_STREAM, parameters=this_parameters)

    values = [event[attribute] for event in event_log if attribute in event]

    return attributes_common.get_kde_numeric_attribute_json(values, parameters=parameters)


def get_kde_date_attribute(log, attribute=DEFAULT_TIMESTAMP_KEY, parameters=None):
    """
    Gets the KDE estimation for the distribution of a date attribute values

    Parameters
    -------------
    log
        Event stream object (if log, is converted)
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

    this_parameters = copy(parameters)
    this_parameters["deepcopy"] = False
    this_parameters["include_case_attributes"] = False

    event_log = log_conversion.apply(log, variant=log_conversion.TO_EVENT_STREAM, parameters=this_parameters)

    values = [strpfromiso.fix_naivety(event[attribute]) for event in event_log if attribute in event]

    return attributes_common.get_kde_date_attribute(values, parameters=parameters)


def get_kde_date_attribute_json(log, attribute=DEFAULT_TIMESTAMP_KEY, parameters=None):
    """
    Gets the KDE estimation for the distribution of a date attribute values
    (expressed as JSON)

    Parameters
    -------------
    log
        Event stream object (if log, is converted)
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

    this_parameters = copy(parameters)
    this_parameters["deepcopy"] = False
    this_parameters["include_case_attributes"] = False

    event_log = log_conversion.apply(log, variant=log_conversion.TO_EVENT_STREAM, parameters=this_parameters)

    values = [strpfromiso.fix_naivety(event[attribute]) for event in event_log if attribute in event]

    return attributes_common.get_kde_date_attribute_json(values, parameters=parameters)

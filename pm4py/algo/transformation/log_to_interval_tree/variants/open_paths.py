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
from enum import Enum
from typing import Optional, Dict, Any, List, Union
import pandas as pd

from intervaltree import IntervalTree, Interval

from pm4py.objects.log.obj import EventLog
from pm4py.util import exec_utils, constants, xes_constants
from pm4py.objects.conversion.log import converter as log_converter


class Parameters(Enum):
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    EPSILON = "epsilon"
    FILTER_ACTIVITY_COUPLE = "filter_activity_couple"


def log_to_intervals(log: Union[EventLog, pd.DataFrame], parameters: Optional[Dict[Any, Any]] = None) -> List[
    List[Any]]:
    """
    Transforms the event log to a list of intervals that are the
    directly-follows paths in the log (open at the complete timestamp of the source event,
    and closed at the start timestamp of the target event).

    Parameters
    -----------------
    log
        Event log
    parameters
        Parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY => the attribute to be used as activity (default: xes_constants.DEFAULT_NAME_KEY)
        - Parameters.START_TIMESTAMP_KEY => the attribute to be used as start timestamp (default: xes_constants.DEFAULT_TIMESTAMP_KEY)
        - Parameters.TIMESTAMP_KEY => the attribute to be used as completion timestamp (default: xes_constants.DEFAULT_TIMESTAMP_KEY)
        - Parameters.EPSILON => the small gap that is removed from the timestamp of the source event and added to the
            timestamp of the target event to make interval querying possible
        - Parameters.FILTER_ACTIVITY_COUPLE => (optional) keeps only the paths between the specified tuple of two activities.

    Returns
    -----------------
    tree
        Interval tree object (which can be queried at a given timestamp, or range of timestamps)
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters,
                                                     xes_constants.DEFAULT_TIMESTAMP_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    filter_activity_couple = exec_utils.get_param_value(Parameters.FILTER_ACTIVITY_COUPLE, parameters, None)

    ret_list = []

    for trace in log:
        for i in range(len(trace) - 1):
            time_i = trace[i][timestamp_key].timestamp()
            for j in range(i + 1, len(trace)):
                time_j = trace[j][start_timestamp_key].timestamp()
                if time_j >= time_i:
                    if filter_activity_couple is None or (
                            trace[i][activity_key] == filter_activity_couple[0] and trace[j][activity_key] ==
                            filter_activity_couple[1]):
                        ret_list.append([time_i, time_j, trace[i], trace[j], trace.attributes])
                    break

    ret_list.sort(key=lambda x: (x[0], x[1], x[2], x[3]))
    return ret_list


def interval_to_tree(intervals: List[List[Any]], parameters: Optional[Dict[Any, Any]] = None) -> IntervalTree:
    """Internal methods to convert the obtained intervals to the eventual IntervalTree"""
    if parameters is None:
        parameters = {}

    epsilon = exec_utils.get_param_value(Parameters.EPSILON, parameters, 0.00001)

    tree = IntervalTree()

    for inte in intervals:
        tree.add(Interval(inte[0] - epsilon, inte[1] + epsilon,
                          data={"source_event": inte[2], "target_event": inte[3], "trace_attributes": inte[4]}))

    return tree


def apply(log: Union[EventLog, pd.DataFrame], parameters: Optional[Dict[Any, Any]] = None) -> IntervalTree:
    """
    Transforms the event log to an interval tree in which the intervals are the
    directly-follows paths in the log (open at the complete timestamp of the source event,
    and closed at the start timestamp of the target event), and having as associated data the source and the target
    event.

    Parameters
    -----------------
    log
        Event log
    parameters
        Parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY => the attribute to be used as activity (default: xes_constants.DEFAULT_NAME_KEY)
        - Parameters.START_TIMESTAMP_KEY => the attribute to be used as start timestamp (default: xes_constants.DEFAULT_TIMESTAMP_KEY)
        - Parameters.TIMESTAMP_KEY => the attribute to be used as completion timestamp (default: xes_constants.DEFAULT_TIMESTAMP_KEY)
        - Parameters.EPSILON => the small gap that is removed from the timestamp of the source event and added to the
            timestamp of the target event to make interval querying possible
        - Parameters.FILTER_ACTIVITY_COUPLE => (optional) keeps only the paths between the specified tuple of two activities.

    Returns
    -----------------
    tree
        Interval tree object (which can be queried at a given timestamp, or range of timestamps)
    """
    intervals = log_to_intervals(log, parameters=parameters)

    return interval_to_tree(intervals, parameters=parameters)

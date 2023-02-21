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
from copy import deepcopy

from pm4py.objects.log.obj import EventLog, Trace
from pm4py.objects.log.util import basic_filter
from pm4py.util import xes_constants as xes
from pm4py.util import constants
import logging


def get_prefixes_from_log(log: EventLog, length: int) -> EventLog:
    """
    Gets the prefixes of a log of a given length

    Parameters
    ----------------
    log
        Event log
    length
        Length

    Returns
    ----------------
    prefix_log
        Log contain the prefixes:
        - if a trace has lower or identical length, it is included as-is
        - if a trace has greater length, it is cut
    """
    prefix_log = EventLog(list(), attributes=log.attributes, extensions=log.extensions, classifiers=log.classifiers,
                            omni_present=log.omni_present, properties=log.properties)
    for trace in log:
        if len(trace) <= length:
            prefix_log.append(trace)
        else:
            new_trace = Trace(attributes=trace.attributes)
            for i in range(length):
                new_trace.append(trace[i])
            prefix_log.append(new_trace)
    return prefix_log


def get_log_with_log_prefixes(log, parameters=None):
    """
    Gets an extended log that contains, in order, all the prefixes for a case of the original log

    Parameters
    --------------
    log
        Original log
    parameters
        Possible parameters of the algorithm

    Returns
    -------------
    all_prefixes_log
        Log with all the prefixes
    change_indexes
        Indexes of the extended log where there was a change between cases
    """
    all_prefixes_log = EventLog()
    change_indexes = []

    for trace in log:
        cumulative_trace = Trace()
        for event in trace:
            all_prefixes_log.append(deepcopy(cumulative_trace))
            cumulative_trace.append(event)
            all_prefixes_log.append(deepcopy(cumulative_trace))
        change_indexes.append([len(all_prefixes_log) - 1] * len(trace))

    return all_prefixes_log, change_indexes


def get_log_traces_to_activities(log, activities, parameters=None):
    """
    Get sublogs taking to each one of the specified activities

    Parameters
    -------------
    log
        Trace log object
    activities
        List of activities in the log
    parameters
        Possible parameters of the algorithm, including:
            PARAMETER_CONSTANT_ACTIVITY_KEY -> activity
            PARAMETER_CONSTANT_TIMESTAMP_KEY -> timestamp

    Returns
    -------------
    list_logs
        List of event logs taking to the first occurrence of each activity
    considered_activities
        All activities that are effectively have been inserted in the list of logs (in some of them, the resulting log
        may be empty)
    """
    if parameters is None:
        parameters = {}

    activity_key = parameters[
        constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY
    parameters[constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY] = activity_key

    list_logs = []
    considered_activities = []
    for act in activities:
        other_acts = [ac for ac in activities if not ac == act]
        parameters_filt1 = deepcopy(parameters)
        parameters_filt2 = deepcopy(parameters)
        parameters_filt1["positive"] = True
        parameters_filt2["positive"] = False
        filtered_log = basic_filter.filter_log_traces_attr(log, [act], parameters=parameters_filt1)
        logging.info("get_log_traces_to_activities activities=" + str(activities) + " act=" + str(
            act) + " 0 len(filtered_log)=" + str(len(filtered_log)))
        filtered_log = basic_filter.filter_log_traces_attr(filtered_log, other_acts, parameters=parameters_filt2)
        logging.info("get_log_traces_to_activities activities=" + str(activities) + " act=" + str(
            act) + " 1 len(filtered_log)=" + str(len(filtered_log)))
        filtered_log, act_durations = get_log_traces_until_activity(filtered_log, act, parameters=parameters)
        logging.info("get_log_traces_to_activities activities=" + str(activities) + " act=" + str(
            act) + " 2 len(filtered_log)=" + str(len(filtered_log)))
        if filtered_log:
            list_logs.append(filtered_log)
            considered_activities.append(act)

    return list_logs, considered_activities


def get_log_traces_until_activity(log, activity, parameters=None):
    """
    Gets a reduced version of the log containing, for each trace, only the events before a
    specified activity

    Parameters
    -------------
    log
        Trace log
    activity
        Activity to reach
    parameters
        Possible parameters of the algorithm, including:
            PARAMETER_CONSTANT_ACTIVITY_KEY -> activity
            PARAMETER_CONSTANT_TIMESTAMP_KEY -> timestamp

    Returns
    -------------
    new_log
        New log
    """
    if parameters is None:
        parameters = {}

    activity_key = parameters[
        constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY
    timestamp_key = parameters[
        constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] if constants.PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else xes.DEFAULT_TIMESTAMP_KEY
    duration_attribute = parameters["duration"] if "duration" in parameters else None
    use_future_attributes = parameters["use_future_attributes"] if "use_future_attributes" in parameters else False

    new_log = EventLog()
    traces_interlapsed_time_to_act = []

    i = 0
    while i < len(log):
        ev_in_tr_w_act = sorted([j for j in range(len(log[i])) if log[i][j][activity_key] == activity])
        if ev_in_tr_w_act and ev_in_tr_w_act[0] > 0:
            new_trace = Trace(log[i][0:ev_in_tr_w_act[0]])
            for attr in log[i].attributes:
                new_trace.attributes[attr] = log[i].attributes[attr]

            if duration_attribute is None:
                try:
                    curr_trace_interlapsed_time_to_act = log[i][ev_in_tr_w_act[0]][timestamp_key].timestamp() - \
                                                         log[i][ev_in_tr_w_act[0] - 1][timestamp_key].timestamp()
                except:
                    curr_trace_interlapsed_time_to_act = log[i][ev_in_tr_w_act[0]][timestamp_key] - \
                                                         log[i][ev_in_tr_w_act[0] - 1][timestamp_key]
                    logging.error("timestamp_key not timestamp")
            else:
                curr_trace_interlapsed_time_to_act = log[i][ev_in_tr_w_act[0]][duration_attribute]

            traces_interlapsed_time_to_act.append(curr_trace_interlapsed_time_to_act)

            if use_future_attributes:
                for j in range(ev_in_tr_w_act[0] + 1, len(log[i])):
                    new_ev = deepcopy(log[i][j])
                    if activity_key in new_ev:
                        del new_ev[activity_key]
                    new_trace.append(new_ev)

            new_log.append(new_trace)
        i = i + 1

    return new_log, traces_interlapsed_time_to_act
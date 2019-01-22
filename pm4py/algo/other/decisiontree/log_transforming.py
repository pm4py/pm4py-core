from copy import deepcopy

from pm4py.algo.filtering.tracelog.attributes import attributes_filter
from pm4py.objects.log.log import TraceLog, Trace
from pm4py.objects.log.util import xes
from pm4py.util import constants


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
        filtered_log = attributes_filter.apply(log, [act], parameters=parameters_filt1)
        filtered_log = attributes_filter.apply(filtered_log, other_acts, parameters=parameters_filt2)
        filtered_log, act_durations = get_log_traces_until_activity(filtered_log, act, parameters=parameters)
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
        New trace log
    """
    if parameters is None:
        parameters = {}

    activity_key = parameters[
        constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY
    timestamp_key = parameters[
        constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] if constants.PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else xes.DEFAULT_TIMESTAMP_KEY

    new_log = TraceLog()
    traces_interlapsed_time_to_act = []

    i = 0
    while i < len(log):
        ev_in_tr_w_act = sorted([j for j in range(len(log[i])) if log[i][j][activity_key] == activity])
        if ev_in_tr_w_act and ev_in_tr_w_act[0] > 0:
            new_trace = Trace(log[i][0:ev_in_tr_w_act[0]])
            for attr in log[i].attributes:
                new_trace.attributes[attr] = log[i].attributes[attr]
            new_log.append(new_trace)
            curr_trace_interlapsed_time_to_act = log[i][ev_in_tr_w_act[0]][timestamp_key].timestamp() - \
                                                 log[i][ev_in_tr_w_act[0] - 1][timestamp_key].timestamp()
            traces_interlapsed_time_to_act.append(curr_trace_interlapsed_time_to_act)
        i = i + 1

    return new_log, traces_interlapsed_time_to_act


def get_all_interlapsed_times_in_activity(log, activity, parameters=None):
    """
    Gets all the interlapsed times in an activity

    Parameters
    ------------
    log
        Trace log object
    activity
        Activity
    parameters
        Possible parameters of the algorithm, including:
            PARAMETER_CONSTANT_ACTIVITY_KEY -> activity
            PARAMETER_CONSTANT_TIMESTAMP_KEY -> timestamp

    Returns
    ------------
    interlapsed_times
        All interlapsed times in the activity
    """

    if parameters is None:
        parameters = {}

    activity_key = parameters[
        constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY
    timestamp_key = parameters[
        constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] if constants.PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else xes.DEFAULT_TIMESTAMP_KEY

    interlapsed_times = []

    i = 0
    while i < len(log):
        ev_in_tr_w_act = sorted([j for j in range(len(log[i])) if log[i][j][activity_key] == activity])
        if ev_in_tr_w_act and ev_in_tr_w_act[0] > 0:
            interlapsed_times.append(
                log[i][ev_in_tr_w_act[0]][timestamp_key].timestamp() - log[i][ev_in_tr_w_act[0] - 1][
                    timestamp_key].timestamp())
        i = i + 1

    interlapsed_times = sorted(interlapsed_times)

    return interlapsed_times


def get_median_time_interlapsed_in_activity(log, activity, parameters=None):
    """
    Gets the median time interlapsed in an activity

    Parameters
    ------------
    log
        Trace log
    activity
        Activity
    parameters
        Possible parameters of the algorithm, including:
            PARAMETER_CONSTANT_ACTIVITY_KEY -> activity
            PARAMETER_CONSTANT_TIMESTAMP_KEY -> timestamp

    Returns
    -------------
    stat
        Statistic value
    """
    stat = 0

    interlapsed_times = get_all_interlapsed_times_in_activity(log, activity, parameters=parameters)

    if interlapsed_times:
        stat = interlapsed_times[int(len(interlapsed_times) / 2)]

    return stat


def get_first_quartile_times_interlapsed_in_activity(log, activity, parameters=None):
    """
    Gets the first quartile of times interlapsed in an activity

    Parameters
    ------------
    log
        Trace log
    activity
        Activity
    parameters
        Possible parameters of the algorithm, including:
            PARAMETER_CONSTANT_ACTIVITY_KEY -> activity
            PARAMETER_CONSTANT_TIMESTAMP_KEY -> timestamp

    Returns
    -------------
    stat
        Statistic value
    """
    stat = 0

    interlapsed_times = get_all_interlapsed_times_in_activity(log, activity, parameters=parameters)

    if interlapsed_times:
        stat = interlapsed_times[int(3 * len(interlapsed_times) / 4)]

    return stat

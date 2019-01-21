from pm4py.objects.log.log import TraceLog, Trace
from pm4py.objects.log.util import xes
from pm4py.util import constants


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

    Returns
    -------------
    new_log
        New trace log
    """
    if parameters is None:
        parameters = {}

    activity_key = parameters[
        constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY

    new_log = TraceLog()

    i = 0
    while i < len(log):
        ev_in_tr_w_act = sorted([j for j in range(len(log[i])) if log[i][j][activity_key] == activity])
        if ev_in_tr_w_act and ev_in_tr_w_act[0] > 0:
            new_trace = Trace(log[i][0:ev_in_tr_w_act[0]])
            for attr in log[i].attributes:
                new_trace.attributes[attr] = log[i].attributes[attr]
            new_log.append(new_trace)
        i = i + 1

    return new_log

from copy import deepcopy

from pm4py.objects.log.log import TraceLog, Trace
from pm4py.objects.log.util import xes
from pm4py.util import constants


def project_tracelog(log, allowed_activities, parameters=None):
    """
    Project a log on a given list of allowed (by the user) activities

    Parameters
    -------------
    log
        Trace log
    allowed_activities
        List of allowed activities
    parameters
        Possible parameters of the algorithm, including:
            PARAMETER_CONSTANT_ACTIVITY_KEY -> the activity name to use in the projection

    Returns
    ------------
    projected_log
        Projected trace log
    """
    if parameters is None:
        parameters = {}
    activity_key = parameters[
        constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY

    projected_log = TraceLog()

    for trace in log:
        projected_trace = Trace()
        for event in trace:
            if event[activity_key] in allowed_activities:
                projected_trace.append(deepcopy(event))
        if len(projected_trace) > 0:
            projected_log.append(projected_trace)

    return projected_log

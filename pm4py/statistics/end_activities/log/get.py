from pm4py.util.xes_constants import DEFAULT_NAME_KEY
from pm4py.statistics.parameters import Parameters
from pm4py.util import exec_utils


def get_end_activities(log, parameters=None):
    """
    Get the end attributes of the log along with their count

    Parameters
    ----------
    log
        Log
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> Attribute key (must be specified if different from concept:name)

    Returns
    ----------
    end_activities
        Dictionary of end attributes associated with their count
    """
    if parameters is None:
        parameters = {}
    attribute_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, DEFAULT_NAME_KEY)

    end_activities = {}

    for trace in log:
        if len(trace) > 0:
            if attribute_key in trace[-1]:
                activity_last_event = trace[-1][attribute_key]
                if activity_last_event not in end_activities:
                    end_activities[activity_last_event] = 0
                end_activities[activity_last_event] = end_activities[activity_last_event] + 1

    return end_activities

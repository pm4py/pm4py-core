from pm4py.util.xes_constants import DEFAULT_NAME_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY


def get_start_activities(log, parameters=None):
    """
    Get the start attributes of the log along with their count

    Parameters
    ----------
    log
        Log
    parameters
        Parameters of the algorithm, including:
            attribute_key -> Attribute key (must be specified if different from concept:name)

    Returns
    ----------
    start_activities
        Dictionary of start attributes associated with their count
    """
    if parameters is None:
        parameters = {}
    attribute_key = parameters[
        PARAMETER_CONSTANT_ACTIVITY_KEY] if PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else DEFAULT_NAME_KEY

    start_activities = {}

    for trace in log:
        if len(trace) > 0:
            if attribute_key in trace[0]:
                activity_first_event = trace[0][attribute_key]
                if activity_first_event not in start_activities:
                    start_activities[activity_first_event] = 0
                start_activities[activity_first_event] = start_activities[activity_first_event] + 1

    return start_activities

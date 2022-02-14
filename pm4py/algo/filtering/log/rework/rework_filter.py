from enum import Enum
from pm4py.util import constants, xes_constants, exec_utils
from pm4py.objects.log.obj import EventLog
from collections import Counter
from typing import Optional, Dict, Any
from pm4py.objects.conversion.log import converter as log_converter


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    MIN_OCCURRENCES = "min_occurrences"
    POSITIVE = "positive"


def apply(log: EventLog, activity: str, parameters: Optional[Dict[Any, Any]] = None) -> EventLog:
    """
    Applies the rework filter on the provided event log and activity.
    This filter the cases of the log having at least Parameters.MIN_OCCURRENCES (default: 2) occurrences
    of the given activity.

    It is also possible (setting Parameters.POSITIVE to False) to retrieve the cases of the log not having the
    given activity or having the activity occurred less than Parameters.MIN_OCCURRENCES times.

    Parameters
    -------------------
    log
        Event log
    activity
        Activity of which the rework shall be filtered
    parameters
        Parameters of the filter, including:
        - Parameters.ACTIVITY_KEY => the attribute to use as activity
        - Parameters.MIN_OCCURRENCES => the minimum number of occurrences for the activity
        - Parameters.POSITIVE => if True, filters the cases of the log having at least MIN_OCCURRENCES occurrences.
            if False, filters the cases of the log where such behavior does not occur.

    Returns
    -----------------
    filtered_log
        Filtered event log
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    min_occurrences = exec_utils.get_param_value(Parameters.MIN_OCCURRENCES, parameters, 2)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)

    filtered_log = EventLog(list(), attributes=log.attributes, extensions=log.extensions, classifiers=log.classifiers,
                            omni_present=log.omni_present, properties=log.properties)

    for trace in log:
        act_counter = Counter([x[activity_key] for x in trace])
        if positive and activity in act_counter and act_counter[activity] >= min_occurrences:
            filtered_log.append(trace)
        elif not positive and (activity not in act_counter or act_counter[activity] < min_occurrences):
            filtered_log.append(trace)

    return filtered_log

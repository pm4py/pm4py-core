import sys
from enum import Enum
from typing import Any, Optional, Dict

from pm4py.objects.conversion.log import converter
from pm4py.objects.log.obj import EventLog
from pm4py.util import constants, xes_constants, exec_utils


class Parameters(Enum):
    ATTRIBUTE_KEY = constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY
    MIN_REP = "min_rep"
    MAX_REP = "max_rep"


def apply(log: EventLog, value: Any, parameters: Optional[Dict[str, Any]] = None) -> EventLog:
    """
    Filters the trace of the log where the given attribute value is repeated
    (in a range of repetitions that is specified by the user)

    Parameters
    ----------------
    log
        Event log
    value
        Value that is investigated
    parameters
        Parameters of the filter, including:
        - Parameters.ATTRIBUTE_KEY => the attribute key
        - Parameters.MIN_REP => minimum number of repetitions
        - Parameters.MAX_REP => maximum number of repetitions

    Returns
    ----------------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}

    log = converter.apply(log, parameters=parameters)

    attribute_key = exec_utils.get_param_value(Parameters.ATTRIBUTE_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    min_rep = exec_utils.get_param_value(Parameters.MIN_REP, parameters, 2)
    max_rep = exec_utils.get_param_value(Parameters.MAX_REP, parameters, sys.maxsize)

    filtered_log = EventLog(list(), attributes=log.attributes, extensions=log.extensions, classifiers=log.classifiers,
                            omni_present=log.omni_present)

    for trace in log:
        rep = 0
        for event in trace:
            if attribute_key in event and event[attribute_key] == value:
                rep += 1
        if min_rep <= rep <= max_rep:
            filtered_log.append(trace)

    return filtered_log

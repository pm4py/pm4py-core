from copy import deepcopy

import pm4py
from pm4py.objects.conversion.log import constants
from pm4py.objects.log import log as log_instance
from pm4py.objects.log.util import general as log_util

DEEPCOPY = constants.DEEPCOPY


def apply(log, parameters=None):
    if isinstance(log, pm4py.objects.log.log.TraceLog):
        parameters = parameters if parameters is not None else dict()
        if log_util.PARAMETER_KEY_CASE_ATTRIBUTE_PRFIX in parameters:
            case_pref = parameters[log_util.PARAMETER_KEY_CASE_ATTRIBUTE_PRFIX]
        else:
            case_pref = log_util.CASE_ATTRIBUTE_PREFIX
        enable_deepcopy = parameters[DEEPCOPY] if DEEPCOPY in parameters else False

        return transform_trace_log_to_event_log(log, include_case_attributes=True,
                                                case_attribute_prefix=case_pref, enable_deepcopy=enable_deepcopy)
    return log


def transform_trace_log_to_event_log(log, include_case_attributes=True,
                                     case_attribute_prefix=log_util.CASE_ATTRIBUTE_PREFIX, enable_deepcopy=False):
    """
    Converts the trace log to an event log

    Parameters
    ----------
    log: :class:`pm4py.log.log.TraceLog`
        A trace Log
    include_case_attributes:
        Default is True
    case_attribute_prefix:
        Default is 'case:'
    enable_deepcopy
        Enables deepcopy (avoid references between input and output objects)

    Returns
        -------
    log : :class:`pm4py.log.log.EventLog`
        An Event log
    """
    if enable_deepcopy:
        log = deepcopy(log)

    events = []
    for trace in log:
        for event in trace:
            if include_case_attributes:
                for key, value in trace.attributes.items():
                    event[case_attribute_prefix + key] = value
            events.append(event)
    return log_instance.EventLog(events, attributes=log.attributes, classifiers=log.classifiers,
                                 omni_present=log.omni_present, extensions=log.extensions)

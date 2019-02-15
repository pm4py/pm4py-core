from copy import deepcopy

import pandas

import pm4py
from pm4py.objects.conversion.log import constants
from pm4py.objects.log import log as log_instance
from pm4py.objects.log.util import general as log_util


DEEPCOPY = constants.DEEPCOPY


def apply(log, parameters=None):
    if isinstance(log, pandas.core.frame.DataFrame):
        log = log_instance.EventStream(log.to_dict('records'), attributes={'origin': 'csv'})
    if isinstance(log, pm4py.objects.log.log.EventLog):
        parameters = parameters if parameters is not None else dict()
        if log_util.PARAMETER_KEY_CASE_ATTRIBUTE_PRFIX in parameters:
            case_pref = parameters[log_util.PARAMETER_KEY_CASE_ATTRIBUTE_PRFIX]
        else:
            case_pref = log_util.CASE_ATTRIBUTE_PREFIX
        enable_deepcopy = parameters[DEEPCOPY] if DEEPCOPY in parameters else False

        return transform_event_log_to_event_stream(log, include_case_attributes=True,
                                                   case_attribute_prefix=case_pref, enable_deepcopy=enable_deepcopy)
    return log


def transform_event_log_to_event_stream(log, include_case_attributes=True,
                                        case_attribute_prefix=log_util.CASE_ATTRIBUTE_PREFIX, enable_deepcopy=False):
    """
    Converts the event log to an event stream

    Parameters
    ----------
    log: :class:`pm4py.log.log.EventLog`
        An Event log
    include_case_attributes:
        Default is True
    case_attribute_prefix:
        Default is 'case:'
    enable_deepcopy
        Enables deepcopy (avoid references between input and output objects)

    Returns
        -------
    log : :class:`pm4py.log.log.EventLog`
        An Event stream
    """
    if enable_deepcopy:
        log = deepcopy(log)

    events = []
    for trace in log:
        for event in trace:
            if include_case_attributes:
                for key, value in trace.attributes.items():
                    event[case_attribute_prefix + key] = value
            # fix 14/02/2019: since the XES standard does not force to specify a case ID, when event log->event stream
            # conversion is done, the possibility to get back the original event log is lost
            if log_util.CASE_ATTRIBUTE_GLUE not in event:
                event[log_util.CASE_ATTRIBUTE_GLUE] = str(hash(trace))
            events.append(event)
    return log_instance.EventStream(events, attributes=log.attributes, classifiers=log.classifiers,
                                    omni_present=log.omni_present, extensions=log.extensions)

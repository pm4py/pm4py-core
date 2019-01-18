import pm4py
from pm4py.objects.log import log as log_instance
from pm4py.objects.log.util import general as log_util

import warnings
import functools


def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.simplefilter('always', DeprecationWarning)  # turn off filter
        warnings.warn("Call to deprecated function {}.".format(func.__name__),
                      category=DeprecationWarning,
                      stacklevel=2)
        warnings.simplefilter('default', DeprecationWarning)  # reset filter
        return func(*args, **kwargs)
    return new_func

@deprecated
def transform_any_log_to_trace_log(log, parameters=None):
    if isinstance(log, pm4py.objects.log.log.EventLog) and (not isinstance(log, pm4py.objects.log.log.TraceLog)):
        parameters = parameters if parameters is not None else dict()
        if log_util.PARAMETER_KEY_CASE_GLUE in parameters:
            glue = parameters[log_util.PARAMETER_KEY_CASE_GLUE]
        else:
            glue = log_util.CASE_ATTRIBUTE_GLUE
        if log_util.PARAMETER_KEY_CASE_ATTRIBUTE_PRFIX in parameters:
            case_pref = parameters[log_util.PARAMETER_KEY_CASE_ATTRIBUTE_PRFIX]
        else:
            case_pref = log_util.CASE_ATTRIBUTE_PREFIX
        return transform_event_log_to_trace_log(log, case_glue=glue, includes_case_attributes=False,
                                                case_attribute_prefix=case_pref)
    return log

@deprecated
def transform_event_log_to_trace_log(log, case_glue=log_util.CASE_ATTRIBUTE_GLUE, includes_case_attributes=True,
                                     case_attribute_prefix=log_util.CASE_ATTRIBUTE_PREFIX):
    """
    Converts the event log to a trace log

    Parameters
    ----------
    log: :class:`pm4py.log.log.EventLog`
        An event Log
    case_glue:
        Case identifier. Default is 'case:concept:name'
    includes_case_attributes:
        Default is True
    case_attribute_prefix:
        Default is 'case:'

    Returns
        -------
    log : :class:`pm4py.log.log.TraceLog`
        A trace log
    """
    traces = {}
    for event in log:
        glue = event[case_glue]
        if glue not in traces:
            trace_attr = {}
            if includes_case_attributes:
                for k in event.keys():
                    if k.startswith(case_attribute_prefix):
                        trace_attr[k.replace(case_attribute_prefix, '')] = event[k]
            traces[glue] = log_instance.Trace(attributes=trace_attr)

        if includes_case_attributes:
            for k in list(event.keys()):
                if k.startswith(case_attribute_prefix):
                    del event[k]

        traces[glue].append(event)
    return log_instance.TraceLog(traces.values(), attributes=log.attributes, classifiers=log.classifiers,
                                 omni_present=log.omni_present, extensions=log.extensions)


def transform_trace_log_to_event_log(log, include_case_attributes=True,
                                     case_attribute_prefix=log_util.CASE_ATTRIBUTE_PREFIX):
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

    Returns
        -------
    log : :class:`pm4py.log.log.EventLog`
        An Event log
    """
    events = []
    for trace in log:
        for event in trace:
            if include_case_attributes:
                for key, value in trace.attributes.items():
                    event[case_attribute_prefix + key] = value
            events.append(event)
    return log_instance.EventLog(events, attributes=log.attributes, classifiers=log.classifiers,
                                 omni_present=log.omni_present, extensions=log.extensions)

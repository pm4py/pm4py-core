from pm4py.objects.log import log as log_instance
from pm4py.objects.log.util import general as log_util

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


def transform_trace_log_to_event_log(log, include_case_attributes=True, case_attribute_prefix=log_util.CASE_ATTRIBUTE_PREFIX):
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

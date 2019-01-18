import pm4py
from pm4py.objects.log import log as log_instance
from pm4py.objects.log.util import general as log_util


def apply(log, parameters=None):
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
        return transform_event_log_to_trace_log(log, case_glue=glue, include_case_attributes=False,
                                                case_attribute_prefix=case_pref)
    return log


def transform_event_log_to_trace_log(log, case_glue=log_util.CASE_ATTRIBUTE_GLUE, include_case_attributes=True,
                                     case_attribute_prefix=log_util.CASE_ATTRIBUTE_PREFIX):
    """
    Converts the event log to a trace log

    Parameters
    ----------
    log: :class:`pm4py.log.log.EventLog`
        An event Log
    case_glue:
        Case identifier. Default is 'case:concept:name'
    include_case_attributes:
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
            if include_case_attributes:
                for k in event.keys():
                    if k.startswith(case_attribute_prefix):
                        trace_attr[k.replace(case_attribute_prefix, '')] = event[k]
            traces[glue] = log_instance.Trace(attributes=trace_attr)

        if include_case_attributes:
            for k in list(event.keys()):
                if k.startswith(case_attribute_prefix):
                    del event[k]

        traces[glue].append(event)
    return log_instance.TraceLog(traces.values(), attributes=log.attributes, classifiers=log.classifiers,
                                 omni_present=log.omni_present, extensions=log.extensions)
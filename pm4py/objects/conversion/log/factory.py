from pm4py.objects.conversion.log.versions import to_event_log, to_trace_log


TO_TRACE_LOG = 'to_trace_log'
TO_EVENT_LOG = 'to_event_log'

VERSIONS = {TO_TRACE_LOG: to_trace_log.apply, TO_EVENT_LOG: to_event_log.apply}


def apply(log, parameters=None, version=TO_TRACE_LOG):
    return VERSIONS[version](log, parameters=parameters)


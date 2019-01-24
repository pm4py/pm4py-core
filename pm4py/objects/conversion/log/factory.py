from pm4py.objects.conversion.log.versions import to_event_log, to_trace_log
from pm4py.objects.conversion.log import constants


TO_TRACE_LOG = constants.TO_TRACE_LOG
TO_EVENT_LOG = constants.TO_EVENT_LOG

DEEPCOPY = constants.DEEPCOPY

VERSIONS = {TO_TRACE_LOG: to_trace_log.apply, TO_EVENT_LOG: to_event_log.apply}


def apply(log, parameters=None, variant=TO_TRACE_LOG):
    return VERSIONS[variant](log, parameters=parameters)


from pm4py.objects.conversion.log import constants
from pm4py.objects.conversion.log.versions import to_event_stream, to_event_log, to_dataframe

TO_TRACE_LOG = constants.TO_TRACE_LOG
TO_EVENT_LOG = constants.TO_EVENT_LOG
TO_EVENT_STREAM = constants.TO_EVENT_STREAM
TO_DATAFRAME = constants.TO_DATAFRAME

DEEPCOPY = constants.DEEPCOPY

VERSIONS = {TO_TRACE_LOG: to_event_log.apply, TO_EVENT_LOG: to_event_log.apply, TO_EVENT_STREAM: to_event_stream.apply,
            TO_DATAFRAME: to_dataframe.apply}


def apply(log, parameters=None, variant=TO_EVENT_LOG):
    return VERSIONS[variant](log, parameters=parameters)

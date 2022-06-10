from enum import Enum

from pm4py.objects.conversion.log.variants import to_event_stream, to_event_log, to_data_frame, to_event_log_wrapped


class Variants(Enum):
    TO_EVENT_LOG = to_event_log
    TO_EVENT_STREAM = to_event_stream
    TO_DATA_FRAME = to_data_frame
    TO_EVENT_LOG_WRAPPED = to_event_log_wrapped


TO_EVENT_LOG = Variants.TO_EVENT_LOG
TO_EVENT_STREAM = Variants.TO_EVENT_STREAM
TO_DATA_FRAME = Variants.TO_DATA_FRAME
TO_EVENT_LOG_WRAPPED = Variants.TO_EVENT_LOG_WRAPPED


def apply(log, parameters=None, variant=None):
    if variant is None:
        variant = Variants.TO_EVENT_LOG
    return variant.value.apply(log, parameters=parameters)

from pm4py.streaming.importer.xes.variants import xes_trace_stream, xes_event_stream
from enum import Enum
from pm4py.util import exec_utils


class Variants(Enum):
    XES_EVENT_STREAM = xes_event_stream
    XES_TRACE_STREAM = xes_trace_stream


DEFAULT_VARIANT = Variants.XES_EVENT_STREAM


def apply(path, variant=DEFAULT_VARIANT, parameters=None):
    """
    Imports a stream from a XES log

    Parameters
    ---------------
    path
        Path to the XES log
    variant
        Variant of the importer:
         - Variants.XES_EVENT_STREAM
         - Variants.XES_TRACE_STREAM

    Returns
    ---------------
    streaming_reader
        Streaming XES reader
    """
    return exec_utils.get_variant(variant).apply(path, parameters=parameters)

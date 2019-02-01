from pm4py.objects.log.log import EventLog


def insert_event_index_as_event_attribute(stream, event_index_attr_name="@@eventindex"):
    """
    Insert the current event index as event attribute

    Parameters
    -----------
    stream
        Stream
    event_index_attr_name
        Attribute name given to the event index
    """

    if not type(stream) is EventLog:
        for i in range(0, len(stream._list)):
            stream._list[i][event_index_attr_name] = i + 1

    return stream


def insert_trace_index_as_event_attribute(log, trace_index_attr_name="@@traceindex"):
    """
    Inserts the current trace index as event attribute
    (overrides previous values if needed)

    Parameters
    -----------
    log
        Log
    trace_index_attr_name
        Attribute name given to the trace index
    """
    for i in range(len(log._list)):
        for j in range(len(log._list[i])):
            log._list[i][j][trace_index_attr_name] = i + 1

    return log

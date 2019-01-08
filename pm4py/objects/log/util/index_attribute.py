from pm4py.objects.log.log import TraceLog


def insert_event_index_as_event_attribute(event_log, event_index_attr_name="@@eventindex"):
    """
    Insert the current event index as event attribute

    Parameters
    -----------
    event_log
        Event log
    event_index_attr_name
        Attribute name given to the event index
    """

    if not type(event_log) is TraceLog:
        for i in range(0, len(event_log._list)):
            event_log._list[i][event_index_attr_name] = i + 1

    return event_log


def insert_trace_index_as_event_attribute(trace_log, trace_index_attr_name="@@traceindex"):
    """
    Inserts the current trace index as event attribute
    (overrides previous values if needed)

    Parameters
    -----------
    trace_log
        Trace log
    trace_index_attr_name
        Attribute name given to the trace index
    """
    for i in range(len(trace_log._list)):
        for j in range(len(trace_log._list[i])):
            trace_log._list[i][j][trace_index_attr_name] = i + 1

    return trace_log

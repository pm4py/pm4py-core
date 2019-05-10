from pm4py.util import constants
from pm4py.objects.log.util import xes
from pm4py.objects.log.log import EventLog, Trace, Event


def apply(log, parameters=None):
    """
    Converts a log from interval format (e.g. an event has two timestamps)
    to lifecycle format (an event has only a timestamp, and a transition lifecycle)

    Parameters
    -------------
    log
        Log (expressed in the interval format)
    parameters
        Possible parameters of the method (activity, timestamp key, start timestamp key, transition ...)

    Returns
    -------------
    log
        Lifecycle event log
    """
    if parameters is None:
        parameters = {}

    timestamp_key = parameters[
        constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] if constants.PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else xes.DEFAULT_TIMESTAMP_KEY
    start_timestamp_key = parameters[
        constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY] if constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY in parameters else xes.DEFAULT_START_TIMESTAMP_KEY
    transition_key = parameters[
        constants.PARAMETER_CONSTANT_TRANSITION_KEY] if constants.PARAMETER_CONSTANT_TRANSITION_KEY in parameters else xes.DEFAULT_TRANSITION_KEY

    if log is not None and len(log) > 0:
        if "PM4PY_TYPE" in log.attributes and log.attributes["PM4PY_TYPE"] == "lifecycle":
            return log
        if log[0] is not None and len(log[0]) > 0:
            first_event = log[0][0]
            if transition_key in first_event:
                return log

        new_log = EventLog()
        new_log.attributes["PM4PY_TYPE"] = "lifecycle"

        for trace in log:
            new_trace = Trace()
            for attr in trace.attributes:
                new_trace.attributes[attr] = trace.attributes[attr]
            list_events = []
            for index, event in enumerate(trace):
                new_event_start = Event()
                new_event_complete = Event()
                for attr in event:
                    if not attr == timestamp_key and not attr == start_timestamp_key:
                        new_event_start[attr] = event[attr]
                        new_event_complete[attr] = event[attr]
                new_event_start[timestamp_key] = event[start_timestamp_key]
                new_event_start[transition_key] = "start"
                new_event_start["@@custom_lif_id"] = 0
                new_event_start["@@origin_ev_idx"] = index
                new_event_complete[timestamp_key] = event[timestamp_key]
                new_event_complete[transition_key] = "complete"
                new_event_complete["@@custom_lif_id"] = 1
                new_event_complete["@@origin_ev_idx"] = index
                list_events.append(new_event_start)
                list_events.append(new_event_complete)
            list_events = sorted(list_events,
                                 key=lambda x: (x[timestamp_key], x["@@origin_ev_idx"], x["@@custom_lif_id"]))
            for ev in list_events:
                new_trace.append(ev)
            new_log.append(new_trace)
        return new_log
    return log

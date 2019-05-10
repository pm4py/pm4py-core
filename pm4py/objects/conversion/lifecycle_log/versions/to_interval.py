from pm4py.util import constants
from pm4py.objects.log.util import xes
from pm4py.objects.log.log import EventLog, Trace, Event


def apply(log, parameters=None):
    """
    Converts a log to interval format (e.g. an event has two timestamps)
    from lifecycle format (an event has only a timestamp, and a transition lifecycle)

    Parameters
    -------------
    log
        Log (expressed in the lifecycle format)
    parameters
        Possible parameters of the method (activity, timestamp key, start timestamp key, transition ...)

    Returns
    -------------
    log
        Interval event log
    """
    if parameters is None:
        parameters = {}

    timestamp_key = parameters[
        constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] if constants.PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else xes.DEFAULT_TIMESTAMP_KEY
    start_timestamp_key = parameters[
        constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY] if constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY in parameters else xes.DEFAULT_START_TIMESTAMP_KEY
    transition_key = parameters[
        constants.PARAMETER_CONSTANT_TRANSITION_KEY] if constants.PARAMETER_CONSTANT_TRANSITION_KEY in parameters else xes.DEFAULT_TRANSITION_KEY
    activity_key = parameters[
        constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY

    if log is not None and len(log) > 0:
        if "PM4PY_TYPE" in log.attributes and log.attributes["PM4PY_TYPE"] == "interval":
            return log
        if log[0] is not None and len(log[0]) > 0:
            first_event = log[0][0]
            if start_timestamp_key in first_event:
                return log

        new_log = EventLog()
        new_log.attributes["PM4PY_TYPE"] = "interval"

        for trace in log:
            new_trace = Trace()
            for attr in trace.attributes:
                new_trace.attributes[attr] = trace.attributes[attr]
            activities_start = {}
            for event in trace:
                activity = event[activity_key]
                transition = event[transition_key]
                timestamp = event[timestamp_key]
                if transition.lower() == "start":
                    if activity not in activities_start:
                        activities_start[activity] = list()
                    activities_start[activity].append(timestamp)
                elif transition.lower() == "complete":
                    start_timestamp = event[timestamp_key]
                    if activity in activities_start and len(activities_start[activity]) > 0:
                        start_timestamp = activities_start[activity].pop(0)
                    new_event = Event()
                    for attr in event:
                        if not attr == timestamp_key and not attr == transition_key:
                            new_event[attr] = event[attr]
                    new_event[start_timestamp_key] = start_timestamp
                    new_event[timestamp_key] = timestamp
                    new_event["@@duration"] = (timestamp - start_timestamp).total_seconds()

                    new_trace.append(new_event)
            new_log.append(new_trace)
        return new_log

    return log

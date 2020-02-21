from pm4py.util.constants import PARAMETER_CONSTANT_ATTRIBUTE_KEY
from pm4py.util.xes_constants import DEFAULT_NAME_KEY
from pm4py.objects.log.log import EventLog, Trace, EventStream
from pm4py.objects.conversion.log import factory as log_conv_fact


def filter_log_events_attr(log, values, parameters=None):
    """
    Filter log by keeping only events with an attribute value that belongs to the provided values list

    Parameters
    -----------
    log
        log
    values
        Allowed attributes
    parameters
        Parameters of the algorithm, including:
            activity_key -> Attribute identifying the activity in the log
            positive -> Indicate if events should be kept/removed

    Returns
    -----------
    filtered_log
        Filtered log
    """

    # CODE SAVING FROM FILTERS

    if parameters is None:
        parameters = {}

    attribute_key = parameters[
        PARAMETER_CONSTANT_ATTRIBUTE_KEY] if PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else DEFAULT_NAME_KEY
    positive = parameters["positive"] if "positive" in parameters else True

    stream = log_conv_fact.apply(log, variant=log_conv_fact.TO_EVENT_STREAM)
    if positive:
        stream = EventStream(list(filter(lambda x: x[attribute_key] in values, stream)))
    else:
        stream = EventStream(list(filter(lambda x: x[attribute_key] not in values, stream)))

    filtered_log = log_conv_fact.apply(stream)

    return filtered_log


def filter_log_traces_attr(log, values, parameters=None):
    """
    Filter log by keeping only traces that has/has not events with an attribute value that belongs to the provided
    values list

    Parameters
    -----------
    log
        Trace log
    values
        Allowed attributes
    parameters
        Parameters of the algorithm, including:
            activity_key -> Attribute identifying the activity in the log
            positive -> Indicate if events should be kept/removed

    Returns
    -----------
    filtered_log
        Filtered log
    """

    # CODE SAVING FROM FILTERS

    if parameters is None:
        parameters = {}

    attribute_key = parameters[
        PARAMETER_CONSTANT_ATTRIBUTE_KEY] if PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else DEFAULT_NAME_KEY
    positive = parameters["positive"] if "positive" in parameters else True

    filtered_log = EventLog()
    for trace in log:
        new_trace = Trace()

        found = False
        for j in range(len(trace)):
            if attribute_key in trace[j]:
                attribute_value = trace[j][attribute_key]
                if attribute_value in values:
                    found = True

        if (found and positive) or (not found and not positive):
            new_trace = trace
        else:
            for attr in trace.attributes:
                new_trace.attributes[attr] = trace.attributes[attr]

        if len(new_trace) > 0:
            filtered_log.append(new_trace)
    return filtered_log

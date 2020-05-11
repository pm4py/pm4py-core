from pm4py.util.constants import PARAMETER_CONSTANT_ATTRIBUTE_KEY
from pm4py.util.xes_constants import DEFAULT_NAME_KEY
from pm4py.objects.log.log import EventLog, Trace, EventStream
from pm4py.objects.conversion.log import converter as log_converter
from enum import Enum
from pm4py.util import exec_utils


class Parameters(Enum):
    ATTRIBUTE_KEY = PARAMETER_CONSTANT_ATTRIBUTE_KEY
    POSITIVE = "positive"


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

    attribute_key = exec_utils.get_param_value(Parameters.ATTRIBUTE_KEY, parameters, DEFAULT_NAME_KEY)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)

    stream = log_converter.apply(log, variant=log_converter.TO_EVENT_STREAM)
    if positive:
        stream = EventStream(list(filter(lambda x: x[attribute_key] in values, stream)))
    else:
        stream = EventStream(list(filter(lambda x: x[attribute_key] not in values, stream)))

    filtered_log = log_converter.apply(stream)

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

    attribute_key = exec_utils.get_param_value(Parameters.ATTRIBUTE_KEY, parameters, DEFAULT_NAME_KEY)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)

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

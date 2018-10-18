from pm4py.algo.filtering.common import filtering_constants
from pm4py.algo.filtering.common.attributes import attributes_common
from pm4py.algo.filtering.tracelog.variants import variants_filter
from pm4py.objects.log.log import TraceLog, Trace
from pm4py.objects.log.util.xes import DEFAULT_NAME_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ATTRIBUTE_KEY, PARAMETER_CONSTANT_ACTIVITY_KEY


def apply_events(trace_log, values, parameters=None):
    """
    Filter log by keeping only events with an attribute value that belongs to the provided values list

    Parameters
    -----------
    trace_log
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
    if parameters is None:
        parameters = {}

    attribute_key = parameters[
        PARAMETER_CONSTANT_ATTRIBUTE_KEY] if PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else DEFAULT_NAME_KEY
    positive = parameters["positive"] if "positive" in parameters else True

    filtered_log = TraceLog()
    for trace in trace_log:
        new_trace = Trace()

        for j in range(len(trace)):
            if attribute_key in trace[j]:
                attribute_value = trace[j][attribute_key]
                if (positive and attribute_value in values) or (not positive and attribute_value not in values):
                    new_trace.append(trace[j])
        if len(new_trace) > 0:
            filtered_log.append(new_trace)
    return filtered_log


def apply(trace_log, values, parameters=None):
    """
    Filter log by keeping only traces that has/has not events with an attribute value that belongs to the provided
    values list

    Parameters
    -----------
    trace_log
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
    if parameters is None:
        parameters = {}

    attribute_key = parameters[
        PARAMETER_CONSTANT_ATTRIBUTE_KEY] if PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else DEFAULT_NAME_KEY
    positive = parameters["positive"] if "positive" in parameters else True

    filtered_log = TraceLog()
    for trace in trace_log:
        new_trace = Trace()

        found = False
        for j in range(len(trace)):
            if attribute_key in trace[j]:
                attribute_value = trace[j][attribute_key]
                if attribute_value in values:
                    found = True

        if (found and positive) or (not found and not positive):
            new_trace = trace

        if len(new_trace) > 0:
            filtered_log.append(new_trace)
    return filtered_log


def get_attribute_values(trace_log, attribute_key, parameters=None):
    """
    Get the attribute values of the log for the specified attribute along with their count

    Parameters
    ----------
    trace_log
        Trace log
    attribute_key
        Attribute for which we would like to know the values along with their count
    parameters
        Possible parameters of the algorithm

    Returns
    ----------
    attributes
        Dictionary of attributes associated with their count
    """
    if parameters is None:
        parameters = {}
    str(parameters)

    attributes = {}

    for trace in trace_log:
        for event in trace:
            if attribute_key in event:
                attribute = event[attribute_key]
                if attribute not in attributes:
                    attributes[attribute] = 0
                attributes[attribute] = attributes[attribute] + 1

    return attributes


def filter_log_by_attributes_threshold(trace_log, attributes, variants, vc, threshold, attribute_key="concept:name"):
    """
    Keep only attributes which number of occurrences is above the threshold (or they belong to the first variant)

    Parameters
    ----------
    trace_log
        Trace log
    attributes
        Dictionary of attributes associated with their count
    variants
        (If specified) Dictionary with variant as the key and the list of traces as the value
    vc
        List of variant names along with their count
    threshold
        Cutting threshold (remove attributes which number of occurrences is below the threshold)
    attribute_key
        (If specified) Specify the activity key in the log (default concept:name)

    Returns
    ----------
    filtered_log
        Filtered log
    """
    filtered_log = TraceLog()
    fva = [x[attribute_key] for x in variants[vc[0][0]][0] if attribute_key in x]
    for trace in trace_log:
        new_trace = Trace()
        for j in range(len(trace)):
            if attribute_key in trace[j]:
                attribute_value = trace[j][attribute_key]
                if attribute_value in attributes:
                    if attribute_value in fva or attributes[attribute_value] >= threshold:
                        new_trace.append(trace[j])
        if len(new_trace) > 0:
            filtered_log.append(new_trace)
    return filtered_log


def apply_auto_filter(trace_log, variants=None, parameters=None):
    """
    Apply an attributes filter detecting automatically a percentage

    Parameters
    ----------
    trace_log
        Trace log
    variants
        (If specified) Dictionary with variant as the key and the list of traces as the value
    parameters
        Parameters of the algorithm, including:
            decreasingFactor -> Decreasing factor (stops the algorithm when the next activity by occurrence is
            below this factor in comparison to previous)
            attribute_key -> Attribute key (must be specified if different from concept:name)

    Returns
    ---------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}
    attribute_key = parameters[
        PARAMETER_CONSTANT_ACTIVITY_KEY] if PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else DEFAULT_NAME_KEY
    decreasing_factor = parameters[
        "decreasingFactor"] if "decreasingFactor" in parameters else filtering_constants.DECREASING_FACTOR

    parameters_variants = {PARAMETER_CONSTANT_ACTIVITY_KEY: attribute_key}
    if variants is None:
        variants = variants_filter.get_variants(trace_log, parameters=parameters_variants)
    vc = variants_filter.get_variants_sorted_by_count(variants)
    activities = get_attribute_values(trace_log, attribute_key, parameters=parameters_variants)
    alist = attributes_common.get_sorted_attributes_list(activities)
    thresh = attributes_common.get_attributes_threshold(alist, decreasing_factor)
    filtered_log = filter_log_by_attributes_threshold(trace_log, activities, variants, vc, thresh, attribute_key)
    return filtered_log

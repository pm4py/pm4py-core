from pm4py.entities.log.log import TraceLog, Trace
from pm4py.algo.filtering.tracelog.variants import variants_filter
from pm4py.util import constants
from pm4py.entities.log.util import xes
from pm4py.algo.filtering.common import filtering_constants


def get_attributes_from_log(trace_log, attribute_key, parameters=None):
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

    attribute_key = parameters[constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY

    attributes = {}

    for trace in trace_log:
        for event in trace:
            if attribute_key in event:
                attribute = event[attribute_key]
                if not attribute in attributes:
                    attributes[attribute] = 0
                attributes[attribute] = attributes[attribute] + 1

    return attributes


def get_sorted_attributes_list(attributes):
    """
    Gets sorted attributes list

    Parameters
    ----------
    attributes
        Dictionary of attributes associated with their count

    Returns
    ----------
    listact
        Sorted end attributes list
    """
    listattr = []
    for a in attributes:
        listattr.append([a, attributes[a]])
    listattr = sorted(listattr, key=lambda x: x[1], reverse=True)
    return listattr


def get_attributes_threshold(attributes, alist, decreasingFactor, maxActivityCount = 25):
    """
    Get attributes cutting threshold

    Parameters
    ----------
    attributes
        Dictionary of attributes associated with their count
    alist
        Sorted attributes list

    Returns
    ---------
    threshold
        Activities cutting threshold
    """

    threshold = alist[0][1]
    i = 1
    while i < len(alist):
        value = alist[i][1]
        if value > threshold * decreasingFactor:
            threshold = value
        if i >= maxActivityCount:
            break
        i = i + 1
    return threshold

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
        j = 0
        while j < len(trace):
            if attribute_key in trace[j]:
                attribute_value = trace[j][attribute_key]
                if attribute_value in attributes:
                    if attribute_value in fva or attributes[attribute_value] >= threshold:
                        new_trace.append(trace[j])
            j = j + 1
        if len(new_trace) > 0:
            filtered_log.append(new_trace)
    return filtered_log

def filter_log_by_specified_attributes(trace_log, attributes_list, attribute_key="concept:name"):
    """
    Filter log by keeping only attributes that belongs to the activity list

    Parameters
    -----------
    trace_log
        Trace log
    attributes_list
        Allowed attributes
    attribute_key
        Activiy key (must be specified if different from concept:name)

    Returns
    -----------
    filtered_log
        Filtered log
    """
    filtered_log = TraceLog()
    for trace in trace_log:
        new_trace = Trace()
        j = 0
        while j < len(trace):
            if attribute_key in trace[j]:
                attribute_value = trace[j][attribute_key]
                if attribute_value in attributes_list:
                    new_trace.append(trace[j])
            j = j + 1
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
            decreasingFactor -> Decreasing factor (stops the algorithm when the next activity by occurrence is below this factor in comparison to previous)
            attribute_key -> Attribute key (must be specified if different from concept:name)

    Returns
    ---------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}
    attribute_key = parameters[constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY
    decreasingFactor = parameters["decreasingFactor"] if "decreasingFactor" in parameters else filtering_constants.DECREASING_FACTOR

    parameters_variants = {constants.PARAMETER_CONSTANT_ACTIVITY_KEY: attribute_key}
    if variants is None:
        variants = variants_filter.get_variants(trace_log, parameters=parameters_variants)
    vc = variants_filter.get_variants_sorted_by_count(variants)
    activities = get_attributes_from_log(trace_log, attribute_key, parameters=parameters_variants)
    alist = get_sorted_attributes_list(activities)
    thresh = get_attributes_threshold(activities, alist, decreasingFactor)
    filtered_log = filter_log_by_attributes_threshold(trace_log, activities, variants, vc, thresh, attribute_key)
    return filtered_log
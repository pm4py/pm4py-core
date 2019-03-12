from pm4py.algo.filtering.common import filtering_constants
from pm4py.algo.filtering.common.attributes import attributes_common
from pm4py.algo.filtering.log.variants import variants_filter
from pm4py.objects.conversion.log import factory as log_conv_fact
from pm4py.objects.log.log import EventLog, Trace
from pm4py.objects.log.util import sampling
from pm4py.objects.log.util import xes
from pm4py.objects.log.util.xes import DEFAULT_NAME_KEY
from pm4py.objects.log.util.xes import DEFAULT_TIMESTAMP_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ATTRIBUTE_KEY, PARAMETER_CONSTANT_ACTIVITY_KEY

DEFAULT_MAX_CASES_FOR_ATTR_SELECTION = 50


def get_all_trace_attributes_from_log(log):
    """
    Get all trace attributes from the log

    Parameters
    ------------
    log
        Log

    Returns
    ------------
    all_attributes
        All trace attributes from the log
    """
    all_attributes = set()
    for trace in log:
        all_attributes = all_attributes.union(set(trace.attributes.keys()))
    if xes.DEFAULT_TRACEID_KEY in all_attributes:
        all_attributes.remove(xes.DEFAULT_TRACEID_KEY)
    return all_attributes


def get_all_event_attributes_from_log(log):
    """
    Get all events attributes from the log

    Parameters
    -------------
    log
        Log

    Returns
    -------------
    all_attributes
        All trace attributes from the log
    """
    all_attributes = set()
    for trace in log:
        for event in trace:
            all_attributes = all_attributes.union(set(event.keys()))
    if xes.DEFAULT_TRANSITION_KEY in all_attributes:
        all_attributes.remove(xes.DEFAULT_TRANSITION_KEY)
    return all_attributes


def select_attributes_from_log_for_tree(log, max_cases_for_attr_selection=DEFAULT_MAX_CASES_FOR_ATTR_SELECTION,
                                        max_diff_occ=DEFAULT_MAX_CASES_FOR_ATTR_SELECTION / 4):
    """
    Select attributes from log for tree

    Parameters
    ------------
    log
        Log
    max_cases_for_attr_selection
        Maximum number of cases to consider for attribute selection
    max_diff_occ
        Maximum number of different occurrences

    Returns
    ------------

    """
    if len(log) > max_cases_for_attr_selection:
        filtered_log = sampling.sample(log, max_cases_for_attr_selection)
    else:
        filtered_log = log
    event_attributes = get_all_event_attributes_from_log(filtered_log)
    trace_attributes = get_all_trace_attributes_from_log(filtered_log)
    event_attributes_values = {}
    trace_attributes_values = {}
    for attr in event_attributes:
        event_attributes_values[attr] = set(get_attribute_values(log, attr).keys())
    for attr in trace_attributes:
        trace_attributes_values[attr] = set(get_trace_attribute_values(log, attr).keys())

    numeric_event_attributes_to_consider = list()
    string_event_attributes_to_consider = list()
    numeric_trace_attributes_to_consider = list()
    string_trace_attributes_to_consider = list()

    for attr in event_attributes_values:
        if type(list(event_attributes_values[attr])[0]) is int or type(list(event_attributes_values[attr])[0]) is float:
            numeric_event_attributes_to_consider.append(attr)
        elif type(list(event_attributes_values[attr])[0]) is str and len(event_attributes_values[attr]) < max_diff_occ:
            string_event_attributes_to_consider.append(attr)

    for attr in trace_attributes_values:
        if type(list(trace_attributes_values[attr])[0]) is int or type(list(trace_attributes_values[attr])[0]) is float:
            numeric_trace_attributes_to_consider.append(attr)
        elif type(list(trace_attributes_values[attr])[0]) is str and len(trace_attributes_values[attr]) < max_diff_occ:
            string_trace_attributes_to_consider.append(attr)

    numeric_event_attributes_to_consider = check_event_attributes_presence(log,
                                                                           numeric_event_attributes_to_consider)
    string_event_attributes_to_consider = check_event_attributes_presence(log,
                                                                          string_event_attributes_to_consider)
    numeric_trace_attributes_to_consider = check_trace_attributes_presence(log,
                                                                           numeric_trace_attributes_to_consider)
    string_trace_attributes_to_consider = check_trace_attributes_presence(log,
                                                                          string_trace_attributes_to_consider)

    return string_trace_attributes_to_consider, string_event_attributes_to_consider, numeric_trace_attributes_to_consider, numeric_event_attributes_to_consider


def check_trace_attributes_presence(log, attributes_set):
    """
    Check trace attributes presence in all the traces of the log

    Parameters
    ------------
    log
        Log
    attributes_set
        Set of attributes

    Returns
    ------------
    filtered_set
        Filtered set of attributes
    """
    keys = list(attributes_set)
    for attr in keys:
        if not verify_if_trace_attribute_is_in_each_trace(log, attr):
            attributes_set.remove(attr)
    return attributes_set


def check_event_attributes_presence(log, attributes_set):
    """
    Check event attributes presence in all the traces of the log

    Parameters
    ------------
    log
        Log
    attributes_set
        Set of attributes

    Returns
    ------------
    filtered_set
        Filtered set of attributes
    """
    keys = list(attributes_set)
    for attr in keys:
        if not verify_if_event_attribute_is_in_each_trace(log, attr):
            attributes_set.remove(attr)
    return attributes_set


def verify_if_event_attribute_is_in_each_trace(log, attribute):
    """
    Verify if the event attribute is in each trace

    Parameters
    ------------
    log
        Log
    attribute
        Attribute

    Returns
    ------------
    boolean
        Boolean value that is aiming to check if the event attribute is in each trace
    """
    for trace in log:
        present = False
        for event in trace:
            if attribute in event:
                present = True
                break
        if not present:
            return False
    return True


def verify_if_trace_attribute_is_in_each_trace(log, attribute):
    """
    Verify if the trace attribute is in each trace

    Parameters
    -------------
    log
        Log
    attribute
        Attribute

    Returns
    ------------
    boolean
        Boolean value that is aiming to check if the trace attribute is in each trace
    """
    for trace in log:
        if attribute not in trace.attributes:
            return False
    return True


def apply_events(log, values, parameters=None):
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
    if parameters is None:
        parameters = {}

    attribute_key = parameters[
        PARAMETER_CONSTANT_ATTRIBUTE_KEY] if PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else DEFAULT_NAME_KEY
    positive = parameters["positive"] if "positive" in parameters else True

    filtered_log = EventLog()
    for trace in log:
        new_trace = Trace()

        for j in range(len(trace)):
            if attribute_key in trace[j]:
                attribute_value = trace[j][attribute_key]
                if (positive and attribute_value in values) or (not positive and attribute_value not in values):
                    new_trace.append(trace[j])
        if len(new_trace) > 0:
            for attr in trace.attributes:
                new_trace.attributes[attr] = trace.attributes[attr]
            filtered_log.append(new_trace)
    return filtered_log


def apply(log, values, parameters=None):
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


def get_attribute_values(log, attribute_key, parameters=None):
    """
    Get the attribute values of the log for the specified attribute along with their count

    Parameters
    ----------
    log
        Log
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

    for trace in log:
        for event in trace:
            if attribute_key in event:
                attribute = event[attribute_key]
                if attribute not in attributes:
                    attributes[attribute] = 0
                attributes[attribute] = attributes[attribute] + 1

    return attributes


def filter_log_on_max_no_activities(log, max_no_activities=25, parameters=None):
    """
    Filter a log on a maximum number of activities

    Parameters
    -------------
    log
        Log
    max_no_activities
        Maximum number of activities
    parameters
        Parameters of the algorithm

    Returns
    -------------
    filtered_log
        Filtered version of the event log
    """
    if parameters is None:
        parameters = {}
    activity_key = parameters[
        PARAMETER_CONSTANT_ACTIVITY_KEY] if PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else DEFAULT_NAME_KEY
    parameters[PARAMETER_CONSTANT_ATTRIBUTE_KEY] = activity_key
    activities = sorted([(x,y) for x,y in get_attribute_values(log, activity_key).items()], key=lambda x: x[1], reverse=True)
    activities = activities[:min(len(activities), max_no_activities)]
    activities = [x[0] for x in activities]
    log = apply_events(log, activities, parameters=parameters)
    return log

def get_trace_attribute_values(log, attribute_key, parameters=None):
    """
    Get the attribute values of the log for the specified attribute along with their count

    Parameters
    ------------
    log
        Log
    attribute_key
        Attribute for which we wish to get the values along with their count
    parameters
        Possible parameters of the algorithm

    Returns
    ------------
    attributes
        Dictionary of attributes associated with their count
    """
    if parameters is None:
        parameters = {}
    str(parameters)

    attributes = {}

    for trace in log:
        if attribute_key in trace.attributes:
            attribute = trace.attributes[attribute_key]
            if attribute not in attributes:
                attributes[attribute] = 0
            attributes[attribute] = attributes[attribute] + 1

    return attributes


def filter_log_by_attributes_threshold(log, attributes, variants, vc, threshold, attribute_key=xes.DEFAULT_NAME_KEY):
    """
    Keep only attributes which number of occurrences is above the threshold (or they belong to the first variant)

    Parameters
    ----------
    log
        Log
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
    filtered_log = EventLog()
    fva = [x[attribute_key] for x in variants[vc[0][0]][0] if attribute_key in x]
    for trace in log:
        new_trace = Trace()
        for j in range(len(trace)):
            if attribute_key in trace[j]:
                attribute_value = trace[j][attribute_key]
                if attribute_value in attributes:
                    if (attribute_value in fva and attribute_key == xes.DEFAULT_NAME_KEY) or attributes[
                        attribute_value] >= threshold:
                        new_trace.append(trace[j])
        if len(new_trace) > 0:
            for attr in trace.attributes:
                new_trace.attributes[attr] = trace.attributes[attr]
            filtered_log.append(new_trace)
    return filtered_log


def apply_auto_filter(log, variants=None, parameters=None):
    """
    Apply an attributes filter detecting automatically a percentage

    Parameters
    ----------
    log
        Log
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
        PARAMETER_CONSTANT_ATTRIBUTE_KEY] if PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else DEFAULT_NAME_KEY
    decreasing_factor = parameters[
        "decreasingFactor"] if "decreasingFactor" in parameters else filtering_constants.DECREASING_FACTOR

    parameters_variants = {PARAMETER_CONSTANT_ATTRIBUTE_KEY: attribute_key,
                           PARAMETER_CONSTANT_ACTIVITY_KEY: attribute_key}
    if variants is None:
        variants = variants_filter.get_variants(log, parameters=parameters_variants)
    vc = variants_filter.get_variants_sorted_by_count(variants)
    attributes_values = get_attribute_values(log, attribute_key, parameters=parameters_variants)
    alist = attributes_common.get_sorted_attributes_list(attributes_values)
    thresh = attributes_common.get_attributes_threshold(alist, decreasing_factor)
    filtered_log = filter_log_by_attributes_threshold(log, attributes_values, variants, vc, thresh, attribute_key)
    return filtered_log


def get_kde_numeric_attribute(log, attribute, parameters=None):
    """
    Gets the KDE estimation for the distribution of a numeric attribute values

    Parameters
    -------------
    log
        Event stream object (if log, is converted)
    attribute
        Numeric attribute to analyse
    parameters
        Possible parameters of the algorithm, including:
            graph_points -> number of points to include in the graph


    Returns
    --------------
    x
        X-axis values to represent
    y
        Y-axis values to represent
    """

    if type(log) is EventLog:
        event_log = log_conv_fact.apply(log, variant=log_conv_fact.TO_EVENT_STREAM)
    else:
        event_log = log

    values = [event[attribute] for event in event_log if attribute in event]

    return attributes_common.get_kde_numeric_attribute(values, parameters=parameters)


def get_kde_numeric_attribute_json(log, attribute, parameters=None):
    """
    Gets the KDE estimation for the distribution of a numeric attribute values
    (expressed as JSON)

    Parameters
    -------------
    log
        Event log object (if log, is converted)
    attribute
        Numeric attribute to analyse
    parameters
        Possible parameters of the algorithm, including:
            graph_points -> number of points to include in the graph


    Returns
    --------------
    x
        X-axis values to represent
    y
        Y-axis values to represent
    """

    if type(log) is EventLog:
        event_log = log_conv_fact.apply(log, variant=log_conv_fact.TO_EVENT_STREAM)
    else:
        event_log = log

    values = [event[attribute] for event in event_log if attribute in event]

    return attributes_common.get_kde_numeric_attribute_json(values, parameters=parameters)


def get_kde_date_attribute(log, attribute=DEFAULT_TIMESTAMP_KEY, parameters=None):
    """
    Gets the KDE estimation for the distribution of a date attribute values

    Parameters
    -------------
    log
        Event stream object (if log, is converted)
    attribute
        Date attribute to analyse
    parameters
        Possible parameters of the algorithm, including:
            graph_points -> number of points to include in the graph


    Returns
    --------------
    x
        X-axis values to represent
    y
        Y-axis values to represent
    """

    if type(log) is EventLog:
        event_log = log_conv_fact.apply(log, variant=log_conv_fact.TO_EVENT_STREAM)
    else:
        event_log = log

    values = [event[attribute].replace(tzinfo=None) for event in event_log if attribute in event]

    return attributes_common.get_kde_date_attribute(values, parameters=parameters)


def get_kde_date_attribute_json(log, attribute=DEFAULT_TIMESTAMP_KEY, parameters=None):
    """
    Gets the KDE estimation for the distribution of a date attribute values
    (expressed as JSON)

    Parameters
    -------------
    log
        Event stream object (if log, is converted)
    attribute
        Date attribute to analyse
    parameters
        Possible parameters of the algorithm, including:
            graph_points -> number of points to include in the graph


    Returns
    --------------
    x
        X-axis values to represent
    y
        Y-axis values to represent
    """

    if type(log) is EventLog:
        event_log = log_conv_fact.apply(log, variant=log_conv_fact.TO_EVENT_STREAM)
    else:
        event_log = log

    values = [event[attribute].replace(tzinfo=None) for event in event_log if attribute in event]

    return attributes_common.get_kde_date_attribute_json(values, parameters=parameters)

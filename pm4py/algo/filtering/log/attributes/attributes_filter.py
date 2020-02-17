from pm4py.algo.filtering.common import filtering_constants
from pm4py.statistics.attributes.common import get as attributes_common
from pm4py.statistics.attributes.log.get import get_attribute_values, get_all_event_attributes_from_log, get_all_trace_attributes_from_log, get_kde_date_attribute, get_kde_date_attribute_json, get_kde_numeric_attribute, get_kde_numeric_attribute_json, get_trace_attribute_values
from pm4py.statistics.attributes.log.select import select_attributes_from_log_for_tree
from pm4py.algo.filtering.log.variants import variants_filter
from pm4py.objects.conversion.log import factory as log_conv_fact
from pm4py.objects.log.log import EventLog, Trace, EventStream
from pm4py.util import xes_constants as xes
from pm4py.util.xes_constants import DEFAULT_NAME_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ATTRIBUTE_KEY, PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_CASEID_KEY


def apply_numeric(log, int1, int2, parameters=None):
    """
    Apply a filter on cases (numerical filter)

    Parameters
    --------------
    log
        Log
    int1
        Lower bound of the interval
    int2
        Upper bound of the interval
    parameters
        Possible parameters of the algorithm

    Returns
    --------------
    filtered_df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}

    attribute_key = parameters[
        PARAMETER_CONSTANT_ATTRIBUTE_KEY] if PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else DEFAULT_NAME_KEY
    case_key = parameters[
        PARAMETER_CONSTANT_CASEID_KEY] if PARAMETER_CONSTANT_CASEID_KEY in parameters else xes.DEFAULT_TRACEID_KEY
    # stream_filter_key is helpful to filter on cases containing an event with an attribute
    # in the specified value set, but such events shall have an activity in particular.
    stream_filter_key1 = parameters["stream_filter_key1"] if "stream_filter_key1" in parameters else None
    stream_filter_value1 = parameters["stream_filter_value1"] if "stream_filter_value1" in parameters else None
    stream_filter_key2 = parameters["stream_filter_key2"] if "stream_filter_key2" in parameters else None
    stream_filter_value2 = parameters["stream_filter_value2"] if "stream_filter_value2" in parameters else None

    positive = parameters["positive"] if "positive" in parameters else True

    stream = log_conv_fact.apply(log, variant=log_conv_fact.TO_EVENT_STREAM)
    if stream_filter_key1 is not None:
        stream = EventStream(
            list(filter(lambda x: stream_filter_key1 in x and x[stream_filter_key1] == stream_filter_value1, stream)))
    if stream_filter_key2 is not None:
        stream = EventStream(
            list(filter(lambda x: stream_filter_key2 in x and x[stream_filter_key2] == stream_filter_value2, stream)))

    if positive:
        stream = EventStream(list(filter(lambda x: attribute_key in x and int1 <= x[attribute_key] <= int2, stream)))
    else:
        stream = EventStream(
            list(filter(lambda x: attribute_key in x and (x[attribute_key] < int1 or x[attribute_key] > int2), stream)))

    all_cases_ids = set(x["case:" + case_key] for x in stream)

    filtered_log = EventLog()

    for case in log:
        if case.attributes[case_key] in all_cases_ids:
            filtered_log.append(case)

    return filtered_log


def apply_numeric_events(log, int1, int2, parameters=None):
    """
    Apply a filter on events (numerical filter)

    Parameters
    --------------
    log
        Log
    int1
        Lower bound of the interval
    int2
        Upper bound of the interval
    parameters
        Possible parameters of the algorithm:
            PARAMETER_CONSTANT_ATTRIBUTE_KEY => indicates which attribute to filter
            positive => keep or remove traces with such events?

    Returns
    --------------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}

    attribute_key = parameters[
        PARAMETER_CONSTANT_ATTRIBUTE_KEY] if PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else DEFAULT_NAME_KEY
    positive = parameters["positive"] if "positive" in parameters else True

    stream = log_conv_fact.apply(log, variant=log_conv_fact.TO_EVENT_STREAM)
    if positive:
        stream = EventStream(list(filter(lambda x: attribute_key in x and int1 <= x[attribute_key] <= int2, stream)))
    else:
        stream = EventStream(
            list(filter(lambda x: attribute_key in x and (x[attribute_key] < int1 or x[attribute_key] > int2), stream)))

    filtered_log = log_conv_fact.apply(stream)

    return filtered_log


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

    stream = log_conv_fact.apply(log, variant=log_conv_fact.TO_EVENT_STREAM)
    if positive:
        stream = EventStream(list(filter(lambda x: x[attribute_key] in values, stream)))
    else:
        stream = EventStream(list(filter(lambda x: x[attribute_key] not in values, stream)))

    filtered_log = log_conv_fact.apply(stream)

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
    all_activities = sorted([(x, y) for x, y in get_attribute_values(log, activity_key).items()], key=lambda x: x[1],
                            reverse=True)
    activities = all_activities[:min(len(all_activities), max_no_activities)]
    activities = [x[0] for x in activities]

    if len(activities) < len(all_activities):
        log = apply_events(log, activities, parameters=parameters)
    return log


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
    if len(log) > 0:
        if variants is None:
            variants = variants_filter.get_variants(log, parameters=parameters_variants)
        vc = variants_filter.get_variants_sorted_by_count(variants)
        attributes_values = get_attribute_values(log, attribute_key, parameters=parameters_variants)
        alist = attributes_common.get_sorted_attributes_list(attributes_values)
        thresh = attributes_common.get_attributes_threshold(alist, decreasing_factor)
        filtered_log = filter_log_by_attributes_threshold(log, attributes_values, variants, vc, thresh, attribute_key)
        return filtered_log
    return log

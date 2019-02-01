from pm4py.algo.filtering.common.filtering_constants import DECREASING_FACTOR
from pm4py.algo.filtering.common.start_activities import start_activities_common
from pm4py.algo.filtering.log.variants import variants_filter
from pm4py.objects.log.log import EventLog
from pm4py.objects.log.util.xes import DEFAULT_NAME_KEY
from pm4py.util import constants
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY


def apply(log, admitted_start_activities, parameters=None):
    """
    Filter the log on the specified start activities

    Parameters
    -----------
    log
        log
    admitted_start_activities
        Admitted start activities
    parameters
        Algorithm parameters

    Returns
    -----------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}
    attribute_key = parameters[
        PARAMETER_CONSTANT_ACTIVITY_KEY] if PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else DEFAULT_NAME_KEY

    filtered_log = [trace for trace in log if trace and trace[0][attribute_key] in admitted_start_activities]
    return filtered_log


def get_start_activities(log, parameters=None):
    """
    Get the start attributes of the log along with their count
    
    Parameters
    ----------
    log
        Log
    parameters
        Parameters of the algorithm, including:
            attribute_key -> Attribute key (must be specified if different from concept:name)
    
    Returns
    ----------
    start_activities
        Dictionary of start attributes associated with their count
    """
    if parameters is None:
        parameters = {}
    attribute_key = parameters[
        PARAMETER_CONSTANT_ACTIVITY_KEY] if PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else DEFAULT_NAME_KEY

    start_activities = {}

    for trace in log:
        if len(trace) > 0:
            if attribute_key in trace[0]:
                activity_first_event = trace[0][attribute_key]
                if activity_first_event not in start_activities:
                    start_activities[activity_first_event] = 0
                start_activities[activity_first_event] = start_activities[activity_first_event] + 1

    return start_activities


def filter_log_by_start_activities(start_activities, variants, vc, threshold, activity_key="concept:name"):
    """
    Keep only variants of the log with a start activity which number of occurrences is above the threshold
    
    Parameters
    ----------
    start_activities
        Dictionary of start attributes associated with their count
    variants
        (If specified) Dictionary with variant as the key and the list of traces as the value
    vc
        List of variant names along with their count
    threshold
        Cutting threshold (remove variants having start attributes which number of occurrences is below the threshold
    activity_key
        (If specified) Specify the activity key in the log (default concept:name)
    
    Returns
    ----------
    filtered_log
        Filtered log
    """
    filtered_log = EventLog()
    fvsa = variants[vc[0][0]][0][0][activity_key]
    for variant in variants:
        vsa = variants[variant][0][0][activity_key]
        if vsa in start_activities:
            if vsa == fvsa or start_activities[vsa] >= threshold:
                for trace in variants[variant]:
                    filtered_log.append(trace)
    return filtered_log


def apply_auto_filter(log, variants=None, parameters=None):
    """
    Apply an end attributes filter detecting automatically a percentage
    
    Parameters
    ----------
    log
        Log
    variants
        (If specified) Dictionary with variant as the key and the list of traces as the value
    parameters
        Parameters of the algorithm, including:
            decreasingFactor -> Decreasing factor (stops the algorithm when the next activity by occurrence is below
            this factor in comparison to previous)
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
        "decreasingFactor"] if "decreasingFactor" in parameters else DECREASING_FACTOR

    parameters_variants = {constants.PARAMETER_CONSTANT_ACTIVITY_KEY: attribute_key}

    if variants is None:
        variants = variants_filter.get_variants(log, parameters=parameters_variants)
    vc = variants_filter.get_variants_sorted_by_count(variants)
    start_activities = get_start_activities(log, parameters=parameters_variants)
    salist = start_activities_common.get_sorted_start_activities_list(start_activities)
    sathreshold = start_activities_common.get_start_activities_threshold(salist, decreasing_factor)
    filtered_log = filter_log_by_start_activities(start_activities, variants, vc, sathreshold, attribute_key)
    return filtered_log

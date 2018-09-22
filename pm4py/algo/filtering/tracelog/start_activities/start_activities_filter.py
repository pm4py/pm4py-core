from pm4py.entities.log.log import TraceLog
from pm4py.algo.filtering.tracelog.variants import variants_filter
from pm4py.entities.log.util import xes
from pm4py.util import constants
from pm4py.algo.filtering.common import filtering_constants
from pm4py.algo.filtering.common.start_activities import start_activities_common

def apply(trace_log, admitted_start_activities, parameters=None):
    """
    Filter the trace log on the specified start activities

    Parameters
    -----------
    trace_log
        Trace log
    admitted_start_activities
        Admitted start activities
    parameters
        Algorithm parameters

    Returns
    -----------
    filtered_log
        Filtered trace log
    """
    if parameters is None:
        parameters = {}
    attribute_key = parameters[constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY

    filtered_log = [trace for trace in trace_log if trace and trace[0][attribute_key] in admitted_start_activities]
    return filtered_log

def get_start_activities(trace_log, parameters=None):
    """
    Get the start attributes of the log along with their count
    
    Parameters
    ----------
    trace_log
        Trace log
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
    attribute_key = parameters[constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY

    start_activities = {}
    
    for trace in trace_log:
        if len(trace) > 0:
            activity_first_event = trace[0][attribute_key]
            if not activity_first_event in start_activities:
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
    filtered_log = TraceLog()
    fvsa = variants[vc[0][0]][0][0][activity_key]
    for variant in variants:
        vsa = variants[variant][0][0][activity_key]
        if vsa in start_activities:
            if vsa == fvsa or start_activities[vsa] >= threshold:
                for trace in variants[variant]:
                    filtered_log.append(trace)
    return filtered_log

def apply_auto_filter(trace_log, variants=None, parameters=None):
    """
    Apply an end attributes filter detecting automatically a percentage
    
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
    start_activities = get_start_activities(trace_log, parameters=parameters_variants)
    salist = start_activities_common.get_sorted_start_activities_list(start_activities)
    sathreshold = start_activities_common.get_start_activities_threshold(start_activities, salist, decreasingFactor)
    filtered_log = filter_log_by_start_activities(start_activities, variants, vc, sathreshold, attribute_key)
    return filtered_log
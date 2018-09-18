from pm4py.log.log import TraceLog
from pm4py.filtering.tracelog.variants import variants_filter
from pm4py.log.util import xes as xes_util
from pm4py.util import constants

def get_start_activities_from_log(trace_log, activity_key="concept:name"):
    """
    Get the start attributes of the log along with their count
    
    Parameters
    ----------
    trace_log
        Trace log
    activity_key
        Activity key (must be specified if different from concept:name)
    
    Returns
    ----------
    start_activities
        Dictionary of start attributes associated with their count
    """
    start_activities = {}
    
    for trace in trace_log:
        if len(trace) > 0:
            activity_first_event = trace[0][activity_key]
            if not activity_first_event in start_activities:
                start_activities[activity_first_event] = 0
            start_activities[activity_first_event] = start_activities[activity_first_event] + 1
    
    return start_activities

def get_sorted_start_activities_list(start_activities):
    """
    Gets sorted start attributes list
    
    Parameters
    ----------
    start_activities
        Dictionary of start attributes associated with their count
    
    Returns
    ----------
    listact
        Sorted start attributes list
    """
    listact = []
    for sa in start_activities:
        listact.append([sa, start_activities[sa]])
    listact = sorted(listact, key=lambda x: x[1], reverse=True)
    return listact

def get_start_activities_threshold(start_activities, salist, decreasingFactor):
    """
    Get start attributes cutting threshold
    
    Parameters
    ----------
    start_activities
        Dictionary of start attributes associated with their count
    salist
        Sorted start attributes list
    
    Returns
    ---------
    threshold
        Start attributes cutting threshold
    """
    threshold = salist[0][1]
    i = 1
    while i < len(salist):
        value = salist[i][1]
        if value > threshold * decreasingFactor:
            threshold = value
        i = i + 1
    return threshold

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

def apply_auto_filter(trace_log, variants=None, decreasingFactor=0.6, activity_key="concept:name"):
    """
    Apply an end attributes filter detecting automatically a percentage
    
    Parameters
    ----------
    trace_log
        Trace log
    variants
        (If specified) Dictionary with variant as the key and the list of traces as the value
    decreasingFactor
        Decreasing factor (stops the algorithm when the next end activity by occurrence is below this factor in comparison to previous)
    activity_key
        Activity key (must be specified if different from concept:name)
    
    Returns
    ---------
    filtered_log
        Filtered log    
    """
    parameters_variants = {constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}

    if variants is None:
        variants = variants_filter.get_variants(trace_log, parameters=parameters_variants)
    vc = variants_filter.get_variants_sorted_by_count(variants)
    start_activities = get_start_activities_from_log(trace_log, activity_key=activity_key)
    salist = get_sorted_start_activities_list(start_activities)
    sathreshold = get_start_activities_threshold(start_activities, salist, decreasingFactor)
    filtered_log = filter_log_by_start_activities(start_activities, variants, vc, sathreshold, activity_key)
    return filtered_log
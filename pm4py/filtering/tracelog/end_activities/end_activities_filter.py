from pm4py.log.log import TraceLog
from pm4py.filtering.tracelog.variants import variants_filter
from pm4py.log.util import xes
from pm4py.util import constants

def get_end_activities_from_log(trace_log, attribute_key="concept:name"):
    """
    Get the end attributes of the log along with their count
    
    Parameters
    ----------
    trace_log
        Trace log
    attribute_key
        Activity key (must be specified if different from concept:name)
    
    Returns
    ----------
    end_activities
        Dictionary of end attributes associated with their count
    """
    end_activities = {}
    
    for trace in trace_log:
        if len(trace) > 0:
            activity_last_event = trace[-1][attribute_key]
            if not activity_last_event in end_activities:
                end_activities[activity_last_event] = 0
            end_activities[activity_last_event] = end_activities[activity_last_event] + 1
    
    return end_activities

def get_sorted_end_activities_list(end_activities):
    """
    Gets sorted end attributes list
    
    Parameters
    ----------
    end_activities
        Dictionary of end attributes associated with their count
    
    Returns
    ----------
    listact
        Sorted end attributes list
    """
    listact = []
    for ea in end_activities:
        listact.append([ea, end_activities[ea]])
    listact = sorted(listact, key=lambda x: x[1], reverse=True)
    return listact

def get_end_activities_threshold(end_activities, ealist, decreasingFactor):
    """
    Get end attributes cutting threshold
    
    Parameters
    ----------
    end_activities
        Dictionary of end attributes associated with their count
    ealist
        Sorted end attributes list
    
    Returns
    ---------
    threshold
        End attributes cutting threshold
    """
    
    threshold = ealist[0][1]
    i = 1
    while i < len(ealist):
        value = ealist[i][1]
        if value > threshold * decreasingFactor:
            threshold = value
        i = i + 1
    return threshold

def filter_log_by_end_activities(end_activities, variants, vc, threshold, activity_key="concept:name"):
    """
    Keep only variants of the log with an end activity which number of occurrences is above the threshold
    
    Parameters
    ----------
    end_activities
        Dictionary of end attributes associated with their count
    variants
        (If specified) Dictionary with variant as the key and the list of traces as the value
    vc
        List of variant names along with their count
    threshold
        Cutting threshold (remove variants having end attributes which number of occurrences is below the threshold
    activity_key
        (If specified) Specify the activity key in the log (default concept:name)
    
    Returns
    ----------
    filtered_log
        Filtered log
    """ 
    filtered_log = TraceLog()
    fvea = variants[vc[0][0]][0][-1][activity_key]    
    for variant in variants:
        vea = variants[variant][0][-1][activity_key]
        if vea in end_activities:
            if vea == fvea or end_activities[vea] >= threshold:
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
    decreasingFactor = parameters["decreasingFactor"] if "decreasingFactor" in parameters else 0.6

    parameters_variants = {constants.PARAMETER_CONSTANT_ACTIVITY_KEY: attribute_key}
    if variants is None:
        variants = variants_filter.get_variants(trace_log, parameters=parameters_variants)
    vc = variants_filter.get_variants_sorted_by_count(variants)
    end_activities = get_end_activities_from_log(trace_log, attribute_key=attribute_key)
    ealist = get_sorted_end_activities_list(end_activities)
    eathreshold = get_end_activities_threshold(end_activities, ealist, decreasingFactor)
    filtered_log = filter_log_by_end_activities(end_activities, variants, vc, eathreshold, attribute_key)

    return filtered_log
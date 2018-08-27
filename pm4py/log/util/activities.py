from pm4py.log.instance import TraceLog, Trace
from pm4py.log.util import variants as variants_module

def get_activities_from_log(trace_log, activity_key="concept:name"):
    """
    Get the activities of the log along with their count

    Parameters
    ----------
    trace_log
        Trace log
    activity_key
        Activity key (must be specified if different from concept:name)

    Returns
    ----------
    activities
        Dictionary of activities associated with their count
    """
    activities = {}

    for trace in trace_log:
        for event in trace:
            activity = event[activity_key]
            if not activity in activities:
                activities[activity] = 0
            activities[activity] = activities[activity] + 1

    return activities


def get_sorted_activities_list(activities):
    """
    Gets sorted activities list

    Parameters
    ----------
    activities
        Dictionary of activities associated with their count

    Returns
    ----------
    listact
        Sorted end activities list
    """
    listact = []
    for a in activities:
        listact.append([a, activities[a]])
    listact = sorted(listact, key=lambda x: x[1], reverse=True)
    return listact


def get_activities_threshold(activities, alist, decreasingFactor, maxActivityCount = 25):
    """
    Get end activities cutting threshold

    Parameters
    ----------
    activities
        Dictionary of activities associated with their count
    alist
        Sorted activities list

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

def filter_log_by_activities(trace_log, activities, variants, vc, threshold, activity_key="concept:name"):
    """
    Keep only activities which number of occurrences is above the threshold (or they belong to the first variant)

    Parameters
    ----------
    trace_log
        Trace log
    activities
        Dictionary of activities associated with their count
    variants
        (If specified) Dictionary with variant as the key and the list of traces as the value
    vc
        List of variant names along with their count
    threshold
        Cutting threshold (remove activities which number of occurrences is below the threshold)
    activity_key
        (If specified) Specify the activity key in the log (default concept:name)

    Returns
    ----------
    filtered_log
        Filtered log
    """
    filtered_log = TraceLog()
    fva = [x[activity_key] for x in variants[vc[0][0]][0]]
    for trace in trace_log:
        new_trace = Trace()
        j = 0
        while j < len(trace):
            activity = trace[j][activity_key]
            if activity in activities:
                if activity in fva or activities[activity] >= threshold:
                    new_trace.append(trace[j])
            j = j + 1
        if len(new_trace) > 0:
            filtered_log.append(new_trace)
    return filtered_log

def apply_auto_filter(trace_log, variants=None, decreasingFactor=0.6, activity_key="concept:name"):
    """
    Apply an activities filter detecting automatically a percentage

    Parameters
    ----------
    trace_log
        Trace log
    variants
        (If specified) Dictionary with variant as the key and the list of traces as the value
    decreasingFactor
        Decreasing factor (stops the algorithm when the next activity by occurrence is below this factor in comparison to previous)
    activity_key
        Activity key (must be specified if different from concept:name)

    Returns
    ---------
    filtered_log
        Filtered log
    """
    if variants is None:
        variants = variants_module.get_variants_from_log(trace_log, activity_key=activity_key)
    vc = variants_module.get_variants_sorted_by_count(variants)
    activities = get_activities_from_log(trace_log, activity_key=activity_key)
    alist = get_sorted_activities_list(activities)
    thresh = get_activities_threshold(activities, alist, decreasingFactor)
    filtered_log = filter_log_by_activities(trace_log, activities, variants, vc, thresh, activity_key)
    return filtered_log
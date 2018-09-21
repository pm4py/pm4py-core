from pm4py.entities.log.log import TraceLog, Trace
from pm4py.algo.filtering.tracelog.variants import variants_filter
from pm4py.util import constants
from pm4py.entities.log.util import xes
from pm4py.algo.filtering.common import filtering_constants


def get_paths_from_log(trace_log, attribute_key="concept:name"):
    """
    Get the paths of the log along with their count

    Parameters
    ----------
    trace_log
        Trace log
    attribute_key
        Attribute key (must be specified if different from concept:name)

    Returns
    ----------
    paths
        Dictionary of paths associated with their count
    """
    paths = {}
    for trace in trace_log:
        i = 0
        while i < len(trace)-1:
            if attribute_key in trace[i] and attribute_key in trace[i+1]:
                path = trace[i][attribute_key] + "," + trace[i + 1][attribute_key]
                if not path in paths:
                    paths[path] = 0
                paths[path] = paths[path] + 1
            i = i + 1
    return paths

def get_sorted_paths_list(paths):
    """
    Gets sorted paths list

    Parameters
    ----------
    paths
        Dictionary of paths associated with their count

    Returns
    ----------
    listpaths
        Sorted paths list
    """
    listpaths = []
    for p in paths:
        listpaths.append([p, paths[p]])
    listpaths = sorted(listpaths, key=lambda x: x[1], reverse=True)
    return listpaths

def get_paths_threshold(paths, plist, decreasingFactor):
    """
    Get end attributes cutting threshold

    Parameters
    ----------
    paths
        Dictionary of paths associated with their count
    listpaths
        Sorted paths list

    Returns
    ---------
    threshold
        Paths cutting threshold
    """

    threshold = plist[0][1]
    i = 1
    while i < len(plist):
        value = plist[i][1]
        if value > threshold * decreasingFactor:
            threshold = value
        i = i + 1
    return threshold

def filter_log_by_paths(trace_log, paths, variants, vc, threshold, attribute_key="concept:name"):
    """
    Keep only paths which number of occurrences is above the threshold (or they belong to the first variant)

    Parameters
    ----------
    trace_log
        Trace log
    paths
        Dictionary of paths associated with their count
    variants
        (If specified) Dictionary with variant as the key and the list of traces as the value
    vc
        List of variant names along with their count
    threshold
        Cutting threshold (remove paths which number of occurrences is below the threshold)
    attribute_key
        (If specified) Specify the attribute key to use (default concept:name)

    Returns
    ----------
    filtered_log
        Filtered log
    """
    filtered_log = TraceLog()
    fvft = variants[vc[0][0]][0]
    fvp = set()
    i = 0
    while i < len(fvft) - 1:
        path = fvft[i][attribute_key] + "," + fvft[i + 1][attribute_key]
        fvp.add(path)
        i = i + 1
    for trace in trace_log:
        new_trace = Trace()
        if len(trace) > 0:
            new_trace.append(trace[0])
            j = 1
            while j < len(trace)-1:
                if attribute_key in trace[j] and attribute_key in trace[j+1]:
                    path = trace[j][attribute_key] + "," + trace[j + 1][attribute_key]
                    if path in paths:
                        if path in fvp or paths[path] >= threshold:
                            new_trace.append(trace[j])
                            new_trace.append(trace[j+1])
                            j = j + 1
                j = j + 1
        if len(trace) > 1 and not j == len(trace):
            new_trace.append(trace[-1])
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
    pths = get_paths_from_log(trace_log, attribute_key=attribute_key)
    plist = get_sorted_paths_list(pths)
    thresh = get_paths_threshold(pths, plist, decreasingFactor)
    filtered_log = filter_log_by_paths(trace_log, pths, variants, vc, thresh, attribute_key)
    return filtered_log
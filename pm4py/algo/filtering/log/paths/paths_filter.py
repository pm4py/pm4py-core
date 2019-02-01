from pm4py.algo.filtering.common import filtering_constants
from pm4py.algo.filtering.log.variants import variants_filter
from pm4py.objects.log.log import EventLog, Trace
from pm4py.objects.log.util import xes
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ATTRIBUTE_KEY


def apply(log, paths, parameters=None):
    """
    Apply a filter on traces containing / not containing a path

    Parameters
    -----------
    log
        Log
    paths
        Paths that we are looking for (expressed as tuple of 2 strings)
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
        PARAMETER_CONSTANT_ATTRIBUTE_KEY] if PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else xes.DEFAULT_NAME_KEY
    positive = parameters["positive"] if "positive" in parameters else True
    filtered_log = EventLog()
    for trace in log:
        found = False
        for i in range(len(trace) - 1):
            path = (trace[i][attribute_key], trace[i + 1][attribute_key])
            if path in paths:
                found = True
                break
        if (found and positive) or (not found and not positive):
            filtered_log.append(trace)
    return filtered_log


def get_paths_from_log(log, attribute_key="concept:name"):
    """
    Get the paths of the log along with their count

    Parameters
    ----------
    log
        Log
    attribute_key
        Attribute key (must be specified if different from concept:name)

    Returns
    ----------
    paths
        Dictionary of paths associated with their count
    """
    paths = {}
    for trace in log:
        for i in range(0, len(trace) - 1):
            if attribute_key in trace[i] and attribute_key in trace[i + 1]:
                path = trace[i][attribute_key] + "," + trace[i + 1][attribute_key]
                if path not in paths:
                    paths[path] = 0
                paths[path] = paths[path] + 1
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


def get_paths_threshold(plist, decreasing_factor):
    """
    Get end attributes cutting threshold

    Parameters
    ----------
    plist
        List of paths ordered by number of occurrences
    decreasing_factor
        Decreasing factor of the algorithm

    Returns
    ---------
    threshold
        Paths cutting threshold
    """

    threshold = plist[0][1]
    for i in range(1, len(plist)):
        value = plist[i][1]
        if value > threshold * decreasing_factor:
            threshold = value
    return threshold


def filter_log_by_paths(log, paths, variants, vc, threshold, attribute_key="concept:name"):
    """
    Keep only paths which number of occurrences is above the threshold (or they belong to the first variant)

    Parameters
    ----------
    log
        Log
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
    filtered_log = EventLog()
    fvft = variants[vc[0][0]][0]
    fvp = set()
    for i in range(0, len(fvft) - 1):
        path = fvft[i][attribute_key] + "," + fvft[i + 1][attribute_key]
        fvp.add(path)
    for trace in log:
        new_trace = Trace()
        jj = 0
        if len(trace) > 0:
            new_trace.append(trace[0])
            for j in range(1, len(trace) - 1):
                jj = j
                if j >= len(trace):
                    break
                if attribute_key in trace[j] and attribute_key in trace[j + 1]:
                    path = trace[j][attribute_key] + "," + trace[j + 1][attribute_key]
                    if path in paths:
                        if path in fvp or paths[path] >= threshold:
                            new_trace.append(trace[j])
                            new_trace.append(trace[j + 1])
        if len(trace) > 1 and not jj == len(trace):
            new_trace.append(trace[-1])
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
        PARAMETER_CONSTANT_ACTIVITY_KEY] if PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY
    decreasing_factor = parameters[
        "decreasingFactor"] if "decreasingFactor" in parameters else filtering_constants.DECREASING_FACTOR

    parameters_variants = {PARAMETER_CONSTANT_ACTIVITY_KEY: attribute_key}
    if variants is None:
        variants = variants_filter.get_variants(log, parameters=parameters_variants)
    vc = variants_filter.get_variants_sorted_by_count(variants)
    pths = get_paths_from_log(log, attribute_key=attribute_key)
    plist = get_sorted_paths_list(pths)
    thresh = get_paths_threshold(plist, decreasing_factor)
    filtered_log = filter_log_by_paths(log, pths, variants, vc, thresh, attribute_key)
    return filtered_log

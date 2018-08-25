from copy import copy, deepcopy
from pm4py.log.instance import TraceLog

def get_variants_from_log(trace_log, activity_key="concept:name"):
    """
    Gets a dictionary whose key is the variant and as value there
    is the list of traces that share the variant

    Parameters
    ----------
    trace_log
        Trace log
    activity_key
        Field that identifies the activity (must be provided if different from concept:name

    Returns
    ----------
    variant
        Dictionary with variant as the key and the list of traces as the value
    """
    variants = {}
    for trace in trace_log:
        variant = ",".join([x[activity_key] for x in trace])
        if not variant in variants:
            variants[variant] = []
        variants[variant].append(trace)
    return variants

def get_variants_sorted_by_count(variants):
    """
    From the dictionary of variants returns an ordered list of variants
    along with their count

    Parameters
    ----------
    variants
        Dictionary with variant as the key and the list of traces as the value

    Returns
    ----------
    var_count
        List of variant names along with their count
    """
    var_count = []
    for variant in variants:
        var_count.append([variant, len(variants[variant])])
    var_count = sorted(var_count, key=lambda x: x[1], reverse=True)
    return var_count

def filter_log_by_variants_percentage(trace_log, variants, variantPercentage=0.0):
    """
    Filter the log by variants percentage

    Parameters
    ----------
    trace_log
        Trace log
    variants
        Dictionary with variant as the key and the list of traces as the value
    variantPercentage
        Percentage of variants that should be kept (the most common variant is always kept)

    Returns
    ----------
    filtered_log
        Filtered trace log
    """
    filtered_log = TraceLog()
    no_of_traces = len(trace_log)
    variant_count = get_variants_sorted_by_count(variants)
    already_added_sum = 0

    i = 0
    while i < len(variant_count):
        variant = variant_count[i][0]
        varcount = variant_count[i][1]
        percentage_already_added = already_added_sum / no_of_traces
        if already_added_sum == 0 or percentage_already_added < variantPercentage:
            for trace in variants[variant]:
                filtered_log.append(trace)
            already_added_sum = already_added_sum + varcount
        i = i + 1

    return filtered_log

def find_auto_threshold(trace_log, variants, decreasingFactor):
    """
    Find automatically variants filtering threshold
    based on specified decreasing factor
    
    Parameters
    ----------
    trace_log
        Trace log
    variants
        Dictionary with variant as the key and the list of traces as the value
    decreasingFactor
        Decreasing factor (stops the algorithm when the next variant by occurrence is below this factor in comparison to previous)
    
    Returns
    ----------
    variantsPercentage
        Percentage of variants to keep in the log
    """
    no_of_traces = len(trace_log)
    variant_count = get_variants_sorted_by_count(variants)
    already_added_sum = 0
    
    prevVarCount = -1
    i = 0
    while i < len(variant_count):
        variant = variant_count[i][0]
        varcount = variant_count[i][1]
        percentage_already_added = already_added_sum / no_of_traces
        if already_added_sum == 0 or varcount > decreasingFactor * prevVarCount:
            already_added_sum = already_added_sum + varcount
        prevVarCount = varcount
        i = i + 1
    
    return percentage_already_added

def apply_auto_filter(trace_log, variants=None, decreasingFactor=0.5, activity_key="concept:name"):
    """
    Apply a variants filter detecting automatically a percentage
    
    Parameters
    ----------
    trace_log
        Trace log
    variants
        (If specified) Dictionary with variant as the key and the list of traces as the value
    decreasingFactor
        Decreasing factor (stops the algorithm when the next variant by occurrence is below this factor in comparison to previous)
    activity_key
        Activity key (must be specified if different from concept:name)
    
    Returns
    ----------
    filteredLog
        Filtered log
    """
    if variants is None:
        variants = get_variants_from_log(trace_log, activity_key=activity_key)
    variantsPercentage = find_auto_threshold(trace_log, variants, decreasingFactor)
    filteredLog = filter_log_by_variants_percentage(trace_log, variants, variantsPercentage)
    return filteredLog
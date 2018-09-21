from pm4py.entities.log.log import TraceLog
from pm4py.entities.log.util import xes
from pm4py.util import constants
from pm4py.algo.filtering.common import filtering_constants


def get_variants(trace_log, parameters=None):
    """
    Gets a dictionary whose key is the variant and as value there
    is the list of traces that share the variant

    Parameters
    ----------
    trace_log
        Trace log
    parameters
        Parameters of the algorithm, including:
            activity_key -> Attribute identifying the activity in the log

    Returns
    ----------
    variant
        Dictionary with variant as the key and the list of traces as the value
    """

    variants_trace_idx = get_variants_from_log_trace_idx(trace_log, parameters=parameters)

    return convert_variants_trace_idx_to_trace_obj(trace_log, variants_trace_idx)

def get_variants_from_log_trace_idx(trace_log, parameters=None):
    """
    Gets a dictionary whose key is the variant and as value there
    is the list of traces indexes that share the variant

    Parameters
    ----------
    trace_log
        Trace log
    parameters
        Parameters of the algorithm, including:
            activity_key -> Attribute identifying the activity in the log

    Returns
    ----------
    variant
        Dictionary with variant as the key and the list of traces indexes as the value
    """

    attribute_key = parameters[constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY

    variants = {}
    for trace_idx, trace in enumerate(trace_log):
        variant = ",".join([x[attribute_key] for x in trace if attribute_key in x])
        if not variant in variants:
            variants[variant] = []
        variants[variant].append(trace_idx)

    return variants

def convert_variants_trace_idx_to_trace_obj(log, variants_trace_idx):
    """
    Converts variants expressed as trace indexes to trace objects

    Parameters
    -----------
    log
        Trace log object
    variants_trace_idx
        Variants associated to a list of belonging indexes

    Returns
    -----------
    variants
        Variants associated to a list of belonging traces
    """
    variants = {}

    for key in variants_trace_idx:
        variants[key] = []
        for value in variants_trace_idx[key]:
            variants[key].append(log[value])

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

def apply_auto_filter(trace_log, variants=None, parameters=None):
    """
    Apply a variants filter detecting automatically a percentage
    
    Parameters
    ----------
    trace_log
        Trace log
    parameters
        Parameters of the algorithm, including:
            activity_key -> Key that identifies the activity
            decreasingFactor -> Decreasing factor (stops the algorithm when the next variant by occurrence is below this factor in comparison to previous)
    
    Returns
    ----------
    filteredLog
        Filtered log
    """
    if parameters is None:
        parameters = {}

    attribute_key = parameters[constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY
    decreasingFactor = parameters["decreasingFactor"] if "decreasingFactor" in parameters else filtering_constants.DECREASING_FACTOR

    parameters_variants = {constants.PARAMETER_CONSTANT_ACTIVITY_KEY: attribute_key}
    if variants is None:
        variants = get_variants(trace_log, parameters=parameters_variants)
    variantsPercentage = find_auto_threshold(trace_log, variants, decreasingFactor)
    filteredLog = filter_log_by_variants_percentage(trace_log, variants, variantsPercentage)
    return filteredLog
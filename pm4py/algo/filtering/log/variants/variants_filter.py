from pm4py.statistics.variants.log.get import get_variants_from_log_trace_idx, get_variants, \
    get_variants_along_with_case_durations, get_variants_sorted_by_count, convert_variants_trace_idx_to_trace_obj
from pm4py.algo.filtering.common import filtering_constants
from pm4py.objects.log.log import EventLog
from pm4py.util.xes_constants import DEFAULT_NAME_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from enum import Enum
from pm4py.util import exec_utils


class Parameters(Enum):
    ACTIVITY_KEY = PARAMETER_CONSTANT_ACTIVITY_KEY
    DECREASING_FACTOR = "decreasingFactor"
    POSITIVE = "positive"


def apply(log, admitted_variants, parameters=None):
    """
    Filter log keeping/removing only provided variants

    Parameters
    -----------
    log
        Log object
    admitted_variants
        Admitted variants
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> Attribute identifying the activity in the log
            Parameters.POSITIVE -> Indicate if events should be kept/removed
    """

    if parameters is None:
        parameters = {}
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)
    variants = get_variants(log, parameters=parameters)
    log = EventLog()
    for variant in variants:
        if (positive and variant in admitted_variants) or (not positive and variant not in admitted_variants):
            for trace in variants[variant]:
                log.append(trace)
    return log


def filter_log_variants_percentage(log, percentage=0.8, parameters=None):
    """
    Filters a log by variants percentage

    Parameters
    -------------
    log
        Event log
    percentage
        Percentage
    parameters
        Parameters of the algorithm

    Returns
    -------------
    filtered_log
        Filtered log (by variants percentage)
    """
    if parameters is None:
        parameters = {}

    variants = get_variants(log, parameters=parameters)

    return filter_variants_variants_percentage(log, variants, variants_percentage=percentage)


def filter_variants_variants_percentage(log, variants, variants_percentage=0.0):
    """
    Filter the log by variants percentage

    Parameters
    ----------
    log
        Log
    variants
        Dictionary with variant as the key and the list of traces as the value
    variants_percentage
        Percentage of variants that should be kept (the most common variant is always kept)

    Returns
    ----------
    filtered_log
        Filtered log
    """
    filtered_log = EventLog()
    no_of_traces = len(log)
    variant_count = get_variants_sorted_by_count(variants)
    already_added_sum = 0
    shall_break_under = -1

    for i in range(len(variant_count)):
        variant = variant_count[i][0]
        varcount = variant_count[i][1]
        if varcount < shall_break_under:
            break
        percentage_already_added = already_added_sum / no_of_traces
        for trace in variants[variant]:
            filtered_log.append(trace)
        already_added_sum = already_added_sum + varcount
        if percentage_already_added >= variants_percentage:
            shall_break_under = varcount

    return filtered_log


def find_auto_threshold(log, variants, decreasing_factor):
    """
    Find automatically variants filtering threshold
    based on specified decreasing factor
    
    Parameters
    ----------
    log
        Log
    variants
        Dictionary with variant as the key and the list of traces as the value
    decreasing_factor
        Decreasing factor (stops the algorithm when the next variant by occurrence is below this factor
        in comparison to previous)
    
    Returns
    ----------
    variantsPercentage
        Percentage of variants to keep in the log
    """
    no_of_traces = len(log)
    variant_count = get_variants_sorted_by_count(variants)
    already_added_sum = 0

    prev_var_count = -1
    percentage_already_added = 0
    for i in range(len(variant_count)):
        varcount = variant_count[i][1]
        percentage_already_added = already_added_sum / no_of_traces
        if already_added_sum == 0 or varcount > decreasing_factor * prev_var_count:
            already_added_sum = already_added_sum + varcount
        else:
            break
        prev_var_count = varcount

    percentage_already_added = already_added_sum / no_of_traces

    return percentage_already_added


def apply_auto_filter(log, variants=None, parameters=None):
    """
    Apply a variants filter detecting automatically a percentage
    
    Parameters
    ----------
    log
        Log
    variants
        Variants contained in the log
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> Key that identifies the activity
            Parameters.DECREASING_FACTOR -> Decreasing factor (stops the algorithm when the next variant by occurrence is below
            this factor in comparison to previous)
    
    Returns
    ----------
    filteredLog
        Filtered log
    """
    if parameters is None:
        parameters = {}

    attribute_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, DEFAULT_NAME_KEY)
    decreasing_factor = exec_utils.get_param_value(Parameters.DECREASING_FACTOR, parameters,
                                                   filtering_constants.DECREASING_FACTOR)

    parameters_variants = {PARAMETER_CONSTANT_ACTIVITY_KEY: attribute_key}
    if variants is None:
        variants = get_variants(log, parameters=parameters_variants)
    variants_percentage = find_auto_threshold(log, variants, decreasing_factor)
    filtered_log = filter_variants_variants_percentage(log, variants, variants_percentage)
    return filtered_log

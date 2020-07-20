from pm4py.util.xes_constants import DEFAULT_NAME_KEY, DEFAULT_TIMESTAMP_KEY
from pm4py.statistics.parameters import Parameters
from pm4py.util import exec_utils
from pm4py.util.constants import DEFAULT_VARIANT_SEP

import numpy as np


def get_language(log, parameters=None):
    """
    Gets the stochastic language of the log (from the variants)

    Parameters
    --------------
    log
        Event log
    parameters
        Parameters

    Returns
    --------------
    dictio
        Dictionary containing the stochastic language of the log
        (variant associated to a number between 0 and 1; the sum is 1)
    """
    vars = get_variants(log, parameters=parameters)
    vars = {tuple(x.split(DEFAULT_VARIANT_SEP)): len(y) for x,y in vars.items()}
    all_values_sum = sum(vars.values())
    for x in vars:
        vars[x] = vars[x] / all_values_sum
    return vars


def get_variants(log, parameters=None):
    """
    Gets a dictionary whose key is the variant and as value there
    is the list of traces that share the variant

    Parameters
    ----------
    log
        Trace log
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> Attribute identifying the activity in the log

    Returns
    ----------
    variant
        Dictionary with variant as the key and the list of traces as the value
    """

    variants_trace_idx = get_variants_from_log_trace_idx(log, parameters=parameters)

    all_var = convert_variants_trace_idx_to_trace_obj(log, variants_trace_idx)

    return all_var


def get_variants_along_with_case_durations(log, parameters=None):
    """
    Gets a dictionary whose key is the variant and as value there
    is the list of traces that share the variant

    Parameters
    ----------
    log
        Trace log
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> Attribute identifying the activity in the log

    Returns
    ----------
    variant
        Dictionary with variant as the key and the list of traces as the value
    """
    if parameters is None:
        parameters = {}

    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY)

    variants_trace_idx = get_variants_from_log_trace_idx(log, parameters=parameters)
    all_var = convert_variants_trace_idx_to_trace_obj(log, variants_trace_idx)

    all_durations = {}

    for var in all_var:
        all_durations[var] = []
        for trace in all_var[var]:
            if trace and timestamp_key in trace[-1] and timestamp_key in trace[0]:
                all_durations[var].append((trace[-1][timestamp_key] - trace[0][timestamp_key]).total_seconds())
            else:
                all_durations[var].append(0)
        all_durations[var] = np.array(all_durations[var])

    return all_var, all_durations


def get_variants_from_log_trace_idx(log, parameters=None):
    """
    Gets a dictionary whose key is the variant and as value there
    is the list of traces indexes that share the variant

    Parameters
    ----------
    log
        Log
    parameters
        Parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> Attribute identifying the activity in the log

    Returns
    ----------
    variant
        Dictionary with variant as the key and the list of traces indexes as the value
    """
    if parameters is None:
        parameters = {}

    attribute_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, DEFAULT_NAME_KEY)

    variants = {}
    for trace_idx, trace in enumerate(log):
        variant = DEFAULT_VARIANT_SEP.join([x[attribute_key] for x in trace if attribute_key in x])
        if variant not in variants:
            variants[variant] = []
        variants[variant].append(trace_idx)

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

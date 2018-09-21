from pm4py.algo.filtering.tracelog.variants import variants_filter as variants_module
from pm4py.algo.filtering.tracelog.paths import paths_filter
from pm4py.algo.filtering.tracelog.start_activities import start_activities_filter
from pm4py.algo.filtering.tracelog.attributes import attributes_filter
from pm4py.algo.filtering.tracelog.end_activities import end_activities_filter
import gc
from pm4py.entities.log.util import xes
from pm4py.util import constants
from pm4py.algo.filtering.common import filtering_constants


def apply_auto_filter(trace_log, parameters=None):
    """
    Apply some filters in battery to the log in order to get a simplified log
    
    Parameters
    ----------
    trace_log
        Trace log
    decreasingFactor
        Decreasing factor (provided to all algorithms)
    activity_key
        Activity key (must be specified if different from concept:name)
    
    Returns
    ---------
    filtered_log
        Filtered log
    """
    
    # the following filters are applied:
    # - activity filter (keep only attributes with a reasonable number of occurrences)
    # - paths filter (keep only paths with a reasonable number of occurrences)
    # - variant filter (keep only variants with a reasonable number of occurrences)
    # - start attributes filter (keep only variants that starts with a plausible start activity)
    # - end attributes filter (keep only variants that starts with a plausible end activity)

    if parameters is None:
        parameters = {}

    if parameters is None:
        parameters = {}

    attribute_key = parameters[constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY
    decreasingFactor = parameters["decreasingFactor"] if "decreasingFactor" in parameters else filtering_constants.DECREASING_FACTOR

    parameters_child = {}
    parameters_child["decreasingFactor"] = decreasingFactor
    parameters_child[constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = attribute_key

    variants = variants_module.get_variants(trace_log, parameters=parameters_child)

    filtered_log1 = attributes_filter.apply_auto_filter(trace_log, variants=variants, parameters=parameters_child)
    trace_log = None
    gc.collect()
    variants = variants_module.get_variants(filtered_log1, parameters=parameters_child)
    filtered_log2 = paths_filter.apply_auto_filter(filtered_log1, variants=variants, parameters=parameters_child)
    filtered_log1 = None
    gc.collect()
    variants = variants_module.get_variants(filtered_log2, parameters=parameters_child)
    filtered_log3 = variants_module.apply_auto_filter(filtered_log2, variants=variants, parameters=parameters_child)
    filtered_log2 = None
    gc.collect()
    filtered_log4 = start_activities_filter.apply_auto_filter(filtered_log3, variants=variants, parameters=parameters_child)
    filtered_log3 = None
    gc.collect()
    filtered_log5 = end_activities_filter.apply_auto_filter(filtered_log4, variants=variants, parameters=parameters_child)
    filtered_log4 = None
    gc.collect()

    return filtered_log5
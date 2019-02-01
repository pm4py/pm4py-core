from pm4py.algo.filtering.common import filtering_constants
from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.algo.filtering.log.end_activities import end_activities_filter
from pm4py.algo.filtering.log.paths import paths_filter
from pm4py.algo.filtering.log.start_activities import start_activities_filter
from pm4py.algo.filtering.log.variants import variants_filter as variants_module
from pm4py.objects.log.util import xes
from pm4py.util import constants
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY


def apply_auto_filter(log, parameters=None):
    """
    Apply some filters in battery to the log in order to get a simplified log
    
    Parameters
    ----------
    log
        Log
    parameters
        Eventual parameters applied to the algorithms:
            decreasingFactor -> Decreasing factor (provided to all algorithms)
            activity_key -> Activity key (must be specified if different from concept:name)
    
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

    attribute_key = parameters[
        PARAMETER_CONSTANT_ACTIVITY_KEY] if PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY
    decreasing_factor = parameters[
        "decreasingFactor"] if "decreasingFactor" in parameters else filtering_constants.DECREASING_FACTOR

    parameters_child = {"decreasingFactor": decreasing_factor, constants.PARAMETER_CONSTANT_ACTIVITY_KEY: attribute_key}

    variants = variants_module.get_variants(log, parameters=parameters_child)

    filtered_log1 = attributes_filter.apply_auto_filter(log, variants=variants, parameters=parameters_child)
    del log
    variants = variants_module.get_variants(filtered_log1, parameters=parameters_child)
    filtered_log2 = paths_filter.apply_auto_filter(filtered_log1, variants=variants, parameters=parameters_child)
    del filtered_log1
    variants = variants_module.get_variants(filtered_log2, parameters=parameters_child)
    filtered_log3 = variants_module.apply_auto_filter(filtered_log2, variants=variants, parameters=parameters_child)
    variants = variants_module.get_variants(filtered_log3, parameters=parameters_child)
    del filtered_log2
    filtered_log4 = start_activities_filter.apply_auto_filter(filtered_log3, variants=variants,
                                                              parameters=parameters_child)
    del filtered_log3
    filtered_log5 = end_activities_filter.apply_auto_filter(filtered_log4, variants=variants,
                                                            parameters=parameters_child)
    del filtered_log4

    return filtered_log5

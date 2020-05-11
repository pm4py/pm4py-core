from pm4py.algo.filtering.common import filtering_constants
from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.algo.filtering.log.end_activities import end_activities_filter
from pm4py.algo.filtering.log.start_activities import start_activities_filter
from pm4py.algo.filtering.log.variants import variants_filter as variants_module
from pm4py.util import xes_constants as xes
from pm4py.util import constants
from enum import Enum
from pm4py.util import exec_utils


class Parameters(Enum):
    ATTRIBUTE_KEY = constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    DECREASING_FACTOR = "decreasingFactor"
    POSITIVE = "positive"
    ENABLE_ACTIVITES_FILTER = "enable_activities_filter"
    ENABLE_VARIANTS_FILTER = "enable_variants_filter"
    ENABLE_START_ACTIVITIES_FILTER = "enable_start_activities_filter"
    ENABLE_END_ACTIVITIES_FILTER = "enable_end_activities_filter"


def apply_auto_filter(log, parameters=None):
    """
    Apply some filters in battery to the log in order to get a simplified log
    
    Parameters
    ----------
    log
        Log
    parameters
        Eventual parameters applied to the algorithms:
            Parameters.DECREASING_FACTOR -> Decreasing factor (provided to all algorithms)
            Parameters.ACTIVITY_KEY -> Activity key (must be specified if different from concept:name)
    
    Returns
    ---------
    filtered_log
        Filtered log
    """

    # the following filters are applied:
    # - activity filter (keep only attributes with a reasonable number of occurrences) (if enabled)
    # - variant filter (keep only variants with a reasonable number of occurrences) (if enabled)
    # - start attributes filter (keep only variants that starts with a plausible start activity) (if enabled)
    # - end attributes filter (keep only variants that starts with a plausible end activity) (if enabled)

    if parameters is None:
        parameters = {}

    enable_activities_filter = exec_utils.get_param_value(Parameters.ENABLE_ACTIVITES_FILTER, parameters, True)
    enable_variants_filter = exec_utils.get_param_value(Parameters.ENABLE_VARIANTS_FILTER, parameters, False)
    enable_start_activities_filter = exec_utils.get_param_value(Parameters.ENABLE_START_ACTIVITIES_FILTER, parameters,
                                                                False)
    enable_end_activities_filter = exec_utils.get_param_value(Parameters.ENABLE_END_ACTIVITIES_FILTER, parameters, True)

    attribute_key = exec_utils.get_param_value(Parameters.ATTRIBUTE_KEY, parameters, xes.DEFAULT_NAME_KEY)

    parameters[Parameters.ATTRIBUTE_KEY] = attribute_key
    parameters[Parameters.ACTIVITY_KEY] = attribute_key

    variants = variants_module.get_variants(log, parameters=parameters)

    filtered_log = log
    if enable_activities_filter:
        filtered_log = attributes_filter.apply_auto_filter(log, variants=variants, parameters=parameters)
        variants = variants_module.get_variants(filtered_log, parameters=parameters)
    if enable_variants_filter:
        filtered_log = variants_module.apply_auto_filter(filtered_log, variants=variants, parameters=parameters)
        variants = variants_module.get_variants(filtered_log, parameters=parameters)
    if enable_start_activities_filter:
        filtered_log = start_activities_filter.apply_auto_filter(filtered_log, variants=variants,
                                                                 parameters=parameters)
    if enable_end_activities_filter:
        filtered_log = end_activities_filter.apply_auto_filter(filtered_log, variants=variants,
                                                               parameters=parameters)

    return filtered_log

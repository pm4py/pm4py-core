from pm4py.log.util import variants as variants_module
from pm4py.log.util import start_activities, end_activities, activities, paths
import gc

def apply_auto_filter(trace_log, decreasingFactor=0.6, activity_key="concept:name"):
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
    # - activity filter (keep only activities with a reasonable number of occurrences)
    # - paths filter (keep only paths with a reasonable number of occurrences)
    # - variant filter (keep only variants with a reasonable number of occurrences)
    # - start activities filter (keep only variants that starts with a plausible start activity)
    # - end activities filter (keep only variants that starts with a plausible end activity)
    variants = variants_module.get_variants_from_log(trace_log, activity_key=activity_key)
    filtered_log1 = activities.apply_auto_filter(trace_log, variants=variants, decreasingFactor=decreasingFactor, activity_key=activity_key)
    trace_log = None
    gc.collect()
    variants = variants_module.get_variants_from_log(filtered_log1, activity_key=activity_key)
    filtered_log2 = paths.apply_auto_filter(filtered_log1, variants=variants, decreasingFactor=decreasingFactor, activity_key=activity_key)
    filtered_log1 = None
    gc.collect()
    variants = variants_module.get_variants_from_log(filtered_log2, activity_key=activity_key)
    filtered_log3 = variants_module.apply_auto_filter(filtered_log2, variants=variants, decreasingFactor=decreasingFactor, activity_key=activity_key)
    filtered_log2 = None
    gc.collect()
    filtered_log4 = start_activities.apply_auto_filter(filtered_log3, variants=variants, decreasingFactor=decreasingFactor, activity_key=activity_key)
    filtered_log3 = None
    gc.collect()
    filtered_log5 = end_activities.apply_auto_filter(filtered_log4, variants=variants, decreasingFactor=decreasingFactor, activity_key=activity_key)
    filtered_log4 = None
    gc.collect()

    return filtered_log5
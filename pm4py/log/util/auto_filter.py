from pm4py.log.util import variants as variants_module
from pm4py.log.util import start_activities, end_activities, activities

def apply_auto_filter(trace_log, decreasingFactor=0.5, activity_key="concept:name"):
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
    # - variant filter (keep only variants with a reasonable number of occurrences)
    # - start activities filter (keep only variants that starts with a plausible start activity)
    # - end activities filter (keep only variants that starts with a plausible end activity)
    variants = variants_module.get_variants_from_log(trace_log, activity_key=activity_key)
    filtered_log1 = activities.apply_auto_filter(trace_log, variants=variants, decreasingFactor=decreasingFactor, activity_key=activity_key)
    variants = variants_module.get_variants_from_log(filtered_log1, activity_key=activity_key)
    filtered_log2 = variants_module.apply_auto_filter(filtered_log1, variants=variants, decreasingFactor=decreasingFactor, activity_key=activity_key)
    filtered_log3 = start_activities.apply_auto_filter(filtered_log2, variants=variants, decreasingFactor=decreasingFactor, activity_key=activity_key)
    filtered_log4 = end_activities.apply_auto_filter(filtered_log3, variants=variants, decreasingFactor=decreasingFactor, activity_key=activity_key)
    
    return filtered_log4
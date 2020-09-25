import deprecation

from pm4py.statistics.passed_time.log.versions import pre, post, prepost

PRE = 'pre'
POST = 'post'
PREPOST = 'prepost'

VERSIONS = {PRE: pre.apply, POST: post.apply, PREPOST: prepost.apply}

@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Use algorithm entrypoint instead (passed_time/log/factory)')
def apply(log, activity, variant=PRE, parameters=None):
    """
    Gets statistics on execution times of the paths to/from the activity

    Parameters
    ------------
    log
        Log
    activity
        Activity
    variant
        Variant
    parameters
        Possible parameters of the algorithm

    Returns
    -----------
    dictio
        Dictio containing the times from/to the activity
    """
    return VERSIONS[variant](log, activity, parameters=parameters)

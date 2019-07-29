from pm4py.statistics.passed_time.pandas.versions import pre, post, prepost

PRE = 'pre'
POST = 'post'
PREPOST = 'prepost'

VERSIONS = {PRE: pre.apply, POST: post.apply, PREPOST: prepost.apply}


def apply(df, activity, variant=PRE, parameters=None):
    """
    Gets statistics on execution times of the paths to/from the activity

    Parameters
    ------------
    df
        Dataframe
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
    return VERSIONS[variant](df, activity, parameters=parameters)

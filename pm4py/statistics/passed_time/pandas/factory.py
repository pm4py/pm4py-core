from pm4py.statistics.passed_time.pandas.versions import pre, post, prepost

PRE = 'pre'
POST = 'post'
PREPOST = 'prepost'

VERSIONS = {PRE: pre.apply, POST: post.apply, PREPOST: prepost.apply}


def apply(df, activity, variant=PRE, parameters=None):
    return VERSIONS[variant](df, activity, parameters=parameters)

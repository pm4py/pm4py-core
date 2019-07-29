from pm4py.statistics.passed_time.pandas.versions import pre, post

PRE = 'pre'
POST = 'post'

VERSIONS = {PRE: pre.apply, POST: post.apply}


def apply(df, activity, variant=PRE, parameters=None):
    return VERSIONS[variant](df, activity, parameters=parameters)

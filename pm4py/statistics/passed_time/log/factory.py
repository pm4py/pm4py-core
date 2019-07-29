from pm4py.statistics.passed_time.log.versions import pre, post

PRE = 'pre'
POST = 'post'

VERSIONS = {PRE: pre.apply, POST: post.apply}


def apply(log, activity, variant=PRE, parameters=None):
    return VERSIONS[variant](log, activity, parameters=parameters)

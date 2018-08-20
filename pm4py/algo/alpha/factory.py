from pm4py.log.util import xes as xes_util
from pm4py.algo.alpha import versions

ALPHA_VERSION_CLASSIC = 'classic'
VERSIONS = {ALPHA_VERSION_CLASSIC: versions.classic.apply}


def apply(log, parameters=None, activity_key=xes_util.DEFAULT_NAME_KEY, variant=ALPHA_VERSION_CLASSIC):
    return VERSIONS[variant](log, parameters, activity_key)

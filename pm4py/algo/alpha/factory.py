from pm4py.log.util import xes as xes_util
from pm4py.algo.alpha import versions
from pm4py import util as pmutil

ALPHA_VERSION_CLASSIC = 'classic'
VERSIONS = {ALPHA_VERSION_CLASSIC: versions.classic.apply}


def apply(log, parameters=None, variant=None):
    if parameters is None:
        parameters = {}
    if not pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY
    if variant is None:
        variant = ALPHA_VERSION_CLASSIC
    return VERSIONS[variant](log, parameters)

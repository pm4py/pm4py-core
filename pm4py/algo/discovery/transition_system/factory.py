import deprecation

from pm4py import util as pmutil
from pm4py.algo.discovery.transition_system.versions import view_based
from pm4py.objects.conversion.log import converter as log_conversion
from pm4py.util import xes_constants as xes_util

VIEW_BASED = "view_based"

VERSIONS = {VIEW_BASED: view_based.apply}

@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Use algorithm entrypoint instead (transition_system/factory)')
def apply(log, parameters=None, variant=VIEW_BASED):
    """
    Find transition system given log

    Parameters
    -----------
    log
        Log
    parameters
        Possible parameters of the algorithm, including:
            view
            window
            direction
    variant
        Variant of the algorithm to use, including:
            view_based

    Returns
    ----------
    ts
        Transition system
    """
    if parameters is None:
        parameters = {}
    if pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY
    if pmutil.constants.PARAMETER_CONSTANT_TIMESTAMP_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] = xes_util.DEFAULT_TIMESTAMP_KEY
    if pmutil.constants.PARAMETER_CONSTANT_CASEID_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_CASEID_KEY] = pmutil.constants.CASE_ATTRIBUTE_GLUE

    return VERSIONS[variant](log_conversion.apply(log, parameters, log_conversion.TO_EVENT_LOG), parameters=parameters)

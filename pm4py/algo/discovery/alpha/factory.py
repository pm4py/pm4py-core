from pm4py.entities.log.util import xes as xes_util
from pm4py.algo.discovery.alpha import versions
from pm4py import util as pmutil

ALPHA_VERSION_CLASSIC = 'classic'
VERSIONS = {ALPHA_VERSION_CLASSIC: versions.classic.apply}
VERSIONS_DFG = {ALPHA_VERSION_CLASSIC: versions.classic.apply_dfg}

def apply(log, parameters=None, variant=ALPHA_VERSION_CLASSIC):
    """
    Apply Alpha Miner to a trace log

    Parameters
    -----------
    log
        Trace log
    variant
        Variant of the algorithm to use (classic)
    parameters
        Possible parameters of the algorithm, including:
            activity key -> Name of the attribute that contains the activity

    Returns
    -----------
    net
        Petri net
    marking
        Initial marking
    final_marking
        Final marking
    """
    if parameters is None:
        parameters = {}
    if not pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY
    return VERSIONS[variant](log, parameters)

def apply_dfg(log, parameters=None, variant=ALPHA_VERSION_CLASSIC):
    """
    Apply Alpha Miner to a DFG graph

    Parameters
    -----------
    dfg
        Directly-Follows graph
    variant
        Variant of the algorithm to use (classic)
    parameters
        Possible parameters of the algorithm, including:
            activity key -> Name of the attribute that contains the activity

    Returns
    -----------
    net
        Petri net
    marking
        Initial marking
    final_marking
        Final marking
    """
    if parameters is None:
        parameters = {}
    if not pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY
    return VERSIONS_DFG[variant](log, parameters)
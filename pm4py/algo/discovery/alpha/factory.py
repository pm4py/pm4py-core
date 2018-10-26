from pm4py import util as pmutil
from pm4py.algo.discovery.alpha import versions
from pm4py.objects.log.util import xes as xes_util

ALPHA_VERSION_CLASSIC = 'classic'
VERSIONS = {ALPHA_VERSION_CLASSIC: versions.classic.apply}
VERSIONS_DFG = {ALPHA_VERSION_CLASSIC: versions.classic.apply_dfg}

DEFAULT_PARAMETERS = {pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: xes_util.DEFAULT_NAME_KEY}


def apply(log, parameters=None, version=ALPHA_VERSION_CLASSIC):
    '''
    Apply the Alpha Miner on top of a trace log

    Parameters
    -----------
    log
        Trace log
    version
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
    '''
    if parameters is None:
        parameters = {}
    if pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY
    return VERSIONS[version](log, parameters)


def apply_dfg(dfg, parameters=None, version=ALPHA_VERSION_CLASSIC):
    '''
    Apply Alpha Miner directly on top of a DFG graph

    Parameters
    -----------
    dfg
        Directly-Follows graph
    version
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
    '''
    if parameters is None:
        parameters = {}
    if pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY
    return VERSIONS_DFG[version](dfg, parameters)

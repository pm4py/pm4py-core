import pandas

from pm4py import util as pmutil
from pm4py.algo.discovery.alpha import versions
from pm4py.algo.discovery.dfg.adapters.pandas import df_statistics
from pm4py.objects.conversion.log import factory as log_conversion
from pm4py.util import xes_constants as xes_util

ALPHA_VERSION_CLASSIC = 'classic'
ALPHA_VERSION_PLUS = 'plus'

VERSIONS = {ALPHA_VERSION_CLASSIC: versions.classic.apply, ALPHA_VERSION_PLUS: versions.plus.apply}
VERSIONS_DFG = {ALPHA_VERSION_CLASSIC: versions.classic.apply_dfg}

DEFAULT_PARAMETERS = {pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: xes_util.DEFAULT_NAME_KEY}


def apply(log, parameters=None, variant=ALPHA_VERSION_CLASSIC):
    """
    Apply the Alpha Miner on top of a log

    Parameters
    -----------
    log
        Log
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
    return VERSIONS[variant](log, parameters=parameters)


def apply_dfg(dfg, parameters=None, variant=ALPHA_VERSION_CLASSIC):
    """
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
    """
    return VERSIONS_DFG[variant](dfg, parameters)

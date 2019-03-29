import pandas

from pm4py import util as pmutil
from pm4py.algo.discovery.alpha import versions
from pm4py.algo.discovery.dfg.adapters.pandas import df_statistics
from pm4py.objects.conversion.log import factory as log_conversion
from pm4py.objects.log.util import xes as xes_util
from pm4py.objects.log.util import general as log_util

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
    if parameters is None:
        parameters = {}
    if pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY
    if pmutil.constants.PARAMETER_CONSTANT_TIMESTAMP_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] = xes_util.DEFAULT_TIMESTAMP_KEY
    if pmutil.constants.PARAMETER_CONSTANT_CASEID_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_CASEID_KEY] = log_util.CASE_ATTRIBUTE_GLUE
    if isinstance(log, pandas.core.frame.DataFrame):
        dfg = df_statistics.get_dfg_graph(log, case_id_glue=parameters[pmutil.constants.PARAMETER_CONSTANT_CASEID_KEY],
                                          activity_key=parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY],
                                          timestamp_key=parameters[pmutil.constants.PARAMETER_CONSTANT_TIMESTAMP_KEY])
        return VERSIONS_DFG[variant](dfg, parameters=parameters)
    return VERSIONS[variant](log_conversion.apply(log, parameters, log_conversion.TO_EVENT_LOG), parameters)


def apply_dfg(dfg, parameters=None, version=ALPHA_VERSION_CLASSIC):
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
    if parameters is None:
        parameters = {}
    if pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY
    return VERSIONS_DFG[version](dfg, parameters)

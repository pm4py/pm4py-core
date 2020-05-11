import pandas

from pm4py import util as pmutil
from pm4py.algo.discovery.parameters import Parameters
from pm4py.algo.discovery.alpha import versions
from pm4py.algo.discovery.dfg.adapters.pandas import df_statistics
from pm4py.objects.conversion.log import converter as log_conversion
from pm4py.util import xes_constants as xes_util
from pm4py.util import exec_utils
from enum import Enum


class Variants(Enum):
    ALPHA_VERSION_CLASSIC = versions.classic
    ALPHA_VERSION_PLUS = versions.plus


ALPHA_VERSION_CLASSIC = Variants.ALPHA_VERSION_CLASSIC
ALPHA_VERSION_PLUS = Variants.ALPHA_VERSION_PLUS
DEFAULT_VARIANT = ALPHA_VERSION_CLASSIC
VERSIONS = {Variants.ALPHA_VERSION_CLASSIC, Variants.ALPHA_VERSION_PLUS}


def apply(log, parameters=None, variant=DEFAULT_VARIANT):
    """
    Apply the Alpha Miner on top of a log

    Parameters
    -----------
    log
        Log
    variant
        Variant of the algorithm to use:
            - Variants.ALPHA_VERSION_CLASSIC
            - Variants.ALPHA_VERSION_PLUS
    parameters
        Possible parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> Name of the attribute that contains the activity

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
    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, pmutil.constants.CASE_CONCEPT_NAME)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_util.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes_util.DEFAULT_TIMESTAMP_KEY)

    if isinstance(log, pandas.core.frame.DataFrame) and variant == ALPHA_VERSION_CLASSIC:
        dfg = df_statistics.get_dfg_graph(log, case_id_glue=case_id_glue,
                                          activity_key=activity_key,
                                          timestamp_key=timestamp_key)
        return exec_utils.get_variant(variant).apply_dfg(dfg, parameters=parameters)
    return exec_utils.get_variant(variant).apply(log_conversion.apply(log, parameters, log_conversion.TO_EVENT_LOG), parameters)


def apply_dfg(dfg, parameters=None, variant=ALPHA_VERSION_CLASSIC):
    """
    Apply Alpha Miner directly on top of a DFG graph

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
    return exec_utils.get_variant(variant).apply_dfg(dfg, parameters)

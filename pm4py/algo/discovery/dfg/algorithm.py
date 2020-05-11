import pandas

from pm4py import util as pmutil
from pm4py.algo.discovery.dfg.adapters.pandas import df_statistics
from pm4py.algo.discovery.dfg.versions import native, performance, freq_triples
from pm4py.objects.conversion.log import converter as log_conversion
from pm4py.objects.log.util import dataframe_utils
from pm4py.util import xes_constants as xes_util
from pm4py.util import exec_utils
from pm4py.algo.discovery.parameters import Parameters
from enum import Enum


class Variants(Enum):
    NATIVE = native
    FREQUENCY = native
    PERFORMANCE = performance
    FREQUENCY_GREEDY = native
    PERFORMANCE_GREEDY = performance
    FREQ_TRIPLES = freq_triples


DFG_NATIVE = Variants.NATIVE
DFG_FREQUENCY = Variants.FREQUENCY
DFG_PERFORMANCE = Variants.PERFORMANCE
DFG_FREQUENCY_GREEDY = Variants.FREQUENCY_GREEDY
DFG_PERFORMANCE_GREEDY = Variants.PERFORMANCE_GREEDY
FREQ_TRIPLES = Variants.FREQ_TRIPLES

DEFAULT_VARIANT = Variants.NATIVE

VERSIONS = {DFG_NATIVE, DFG_FREQUENCY, DFG_PERFORMANCE, DFG_FREQUENCY_GREEDY, DFG_PERFORMANCE_GREEDY, FREQ_TRIPLES}


def apply(log, parameters=None, variant=DEFAULT_VARIANT):
    """
    Calculates DFG graph (frequency or performance) starting from a log

    Parameters
    ----------
    log
        Log
    parameters
        Possible parameters passed to the algorithms:
            Parameters.AGGREGATION_MEASURE -> performance aggregation measure (min, max, mean, median)
            Parameters.ACTIVITY_KEY -> Attribute to use as activity
            Parameters.TIMESTAMP_KEY -> Attribute to use as timestamp
    variant
        Variant of the algorithm to use, possible values:
            - Variants.NATIVE
            - Variants.FREQUENCY
            - Variants.FREQUENCY_GREEDY
            - Variants.PERFORMANCE
            - Variants.PERFORMANCE_GREEDY
            - Variants.FREQ_TRIPLES

    Returns
    -------
    dfg
        DFG graph
    """
    if parameters is None:
        parameters = {}
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_util.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes_util.DEFAULT_TIMESTAMP_KEY)
    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, pmutil.constants.CASE_CONCEPT_NAME)

    if isinstance(log, pandas.core.frame.DataFrame) and not variant == Variants.FREQ_TRIPLES:
        log = dataframe_utils.convert_timestamp_columns_in_df(log, timest_columns=[
            timestamp_key])
        dfg_frequency, dfg_performance = df_statistics.get_dfg_graph(log, measure="both",
                                                                     activity_key=activity_key,
                                                                     timestamp_key=timestamp_key,
                                                                     case_id_glue=case_id_glue)
        if variant in [Variants.PERFORMANCE, Variants.PERFORMANCE_GREEDY]:
            return dfg_performance
        else:
            return dfg_frequency
    return exec_utils.get_variant(variant).apply(log_conversion.apply(log, parameters, log_conversion.TO_EVENT_LOG), parameters=parameters)

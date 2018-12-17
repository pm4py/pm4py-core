from pm4py.algo.discovery.dfg.adapters.pandas import df_statistics as dfg_util
from pm4py.algo.filtering.common.filtering_constants import CASE_CONCEPT_NAME
from pm4py.algo.filtering.pandas.variants import variants_filter
from pm4py.objects.log.util.xes import DEFAULT_NAME_KEY
from pm4py.objects.log.util.xes import DEFAULT_TIMESTAMP_KEY
from pm4py.statistics.traces.pandas import case_statistics
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_CASEID_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_TIMESTAMP_KEY
from pm4py.algo.discovery.alpha import factory as alpha_miner


def apply(df, parameters=None):
    if parameters is None:
        parameters = {}

    CASEID_GLUE = parameters[
        PARAMETER_CONSTANT_CASEID_KEY] if PARAMETER_CONSTANT_CASEID_KEY in parameters else CASE_CONCEPT_NAME
    ACTIVITY_KEY = parameters[
        PARAMETER_CONSTANT_ACTIVITY_KEY] if PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else DEFAULT_NAME_KEY
    TIMEST_KEY = parameters[
        PARAMETER_CONSTANT_TIMESTAMP_KEY] if PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else DEFAULT_TIMESTAMP_KEY

    discovery_algorithm = parameters["discovery_algorithm"] if "discovery_algorithm" in parameters else "alphaclassic"
    max_no_variants = parameters["max_no_variants"] if "max_no_variants" in parameters else 20

    variants_df = case_statistics.get_variants_df(df, parameters=parameters)
    parameters["variants_df"] = variants_df

    variant_stats = case_statistics.get_variants_statistics(df, parameters=parameters)

    all_variants_list = []
    for var in variant_stats:
        all_variants_list.append([var["variant"], var[CASEID_GLUE]])

    all_variants_list = sorted(all_variants_list, key=lambda x: x[1], reverse=True)

    considered_variants = []

    i = 0
    while i < min(len(all_variants_list), max_no_variants):
        variant = all_variants_list[i][0]
        considered_variants.append(variant)

        trace_of_this_variant = variants_filter.apply(df, [variant]).groupby()
        filtered_df = variants_filter.apply(df, considered_variants)

        dfg_frequency = dfg_util.get_dfg_graph(filtered_df, measure="frequency",
                                               perf_aggregation_key="median",
                                               case_id_glue=CASEID_GLUE,
                                               activity_key=ACTIVITY_KEY,
                                               timestamp_key=TIMEST_KEY)

        net, initial_marking, final_marking = alpha_miner.apply_dfg(dfg_frequency, parameters=parameters)



        i = i + 1

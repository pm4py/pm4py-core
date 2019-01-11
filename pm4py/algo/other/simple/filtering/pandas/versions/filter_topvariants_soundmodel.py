from pm4py.algo.conformance.alignments import factory as alignment_factory
from pm4py.algo.discovery.alpha import factory as alpha_miner
from pm4py.algo.discovery.dfg.adapters.pandas import df_statistics as dfg_util
from pm4py.algo.filtering.common.filtering_constants import CASE_CONCEPT_NAME
from pm4py.algo.filtering.pandas.variants import variants_filter
from pm4py.evaluation.replay_fitness import factory as replay_fitness_factory
from pm4py.objects.log import transform
from pm4py.objects.log.importer.csv.versions import pandas_df_imp
from pm4py.objects.log.log import TraceLog
from pm4py.objects.log.util.xes import DEFAULT_NAME_KEY
from pm4py.objects.log.util.xes import DEFAULT_TIMESTAMP_KEY
from pm4py.objects.petri import check_soundness
from pm4py.statistics.traces.pandas import case_statistics
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ATTRIBUTE_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_CASEID_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_TIMESTAMP_KEY


def apply(df, parameters=None):
    """
    Returns a Pandas dataframe from which a sound workflow net could be extracted taking into account
    a discovery algorithm returning models only with visible transitions

    Parameters
    ------------
    df
        Pandas dataframe
    parameters
        Possible parameters of the algorithm, including:
            max_no_variants -> Maximum number of variants to consider to return a Petri net

    Returns
    ------------
    filtered_df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}

    if PARAMETER_CONSTANT_CASEID_KEY not in parameters:
        parameters[PARAMETER_CONSTANT_CASEID_KEY] = CASE_CONCEPT_NAME
    if PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters:
        parameters[PARAMETER_CONSTANT_ACTIVITY_KEY] = DEFAULT_NAME_KEY
    if PARAMETER_CONSTANT_TIMESTAMP_KEY not in parameters:
        parameters[PARAMETER_CONSTANT_TIMESTAMP_KEY] = DEFAULT_TIMESTAMP_KEY
    if PARAMETER_CONSTANT_ATTRIBUTE_KEY not in parameters:
        parameters[PARAMETER_CONSTANT_ATTRIBUTE_KEY] = parameters[PARAMETER_CONSTANT_ACTIVITY_KEY]

    caseid_glue = parameters[PARAMETER_CONSTANT_CASEID_KEY]
    activity_key = parameters[PARAMETER_CONSTANT_ACTIVITY_KEY]
    timest_key = parameters[PARAMETER_CONSTANT_TIMESTAMP_KEY]

    max_no_variants = parameters["max_no_variants"] if "max_no_variants" in parameters else 20

    variants_df = case_statistics.get_variants_df(df, parameters=parameters)
    parameters["variants_df"] = variants_df

    variant_stats = case_statistics.get_variant_statistics(df, parameters=parameters)

    all_variants_list = []
    for var in variant_stats:
        all_variants_list.append([var["variant"], var[caseid_glue]])

    all_variants_list = sorted(all_variants_list, key=lambda x: (x[1], x[0]), reverse=True)

    considered_variants = []
    considered_traces = []

    i = 0
    while i < min(len(all_variants_list), max_no_variants):
        variant = all_variants_list[i][0]

        considered_variants.append(variant)

        filtered_df = variants_filter.apply(df, considered_variants, parameters=parameters)

        dfg_frequency = dfg_util.get_dfg_graph(filtered_df, measure="frequency",
                                               perf_aggregation_key="median",
                                               case_id_glue=caseid_glue,
                                               activity_key=activity_key,
                                               timestamp_key=timest_key)

        net, initial_marking, final_marking = alpha_miner.apply_dfg(dfg_frequency, parameters=parameters)

        is_sound = check_soundness.check_petri_wfnet_and_soundness(net)
        if not is_sound:
            del considered_variants[-1]
        else:
            traces_of_this_variant = variants_filter.apply(df, [variant], parameters=parameters).groupby(caseid_glue)
            traces_of_this_variant_keys = list(traces_of_this_variant.groups.keys())
            trace_of_this_variant = traces_of_this_variant.get_group(traces_of_this_variant_keys[0])

            this_trace = transform.transform_event_log_to_trace_log(
                pandas_df_imp.convert_dataframe_to_event_log(trace_of_this_variant), case_glue=caseid_glue)[0]
            if not activity_key == DEFAULT_NAME_KEY:
                for j in range(len(this_trace)):
                    this_trace[j][DEFAULT_NAME_KEY] = this_trace[j][activity_key]
            considered_traces.append(this_trace)
            filtered_log = TraceLog(considered_traces)

            try:
                alignments = alignment_factory.apply(filtered_log, net, initial_marking, final_marking)
                del alignments
                fitness = replay_fitness_factory.apply(filtered_log, net, initial_marking, final_marking,
                                                       parameters=parameters)
                if fitness["log_fitness"] < 0.99999:
                    del considered_variants[-1]
                    del considered_traces[-1]
            except TypeError:
                del considered_variants[-1]
                del considered_traces[-1]

        i = i + 1

    return variants_filter.apply(df, considered_variants, parameters=parameters)

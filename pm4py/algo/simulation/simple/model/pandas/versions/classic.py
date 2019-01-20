from pm4py.algo.discovery.alpha import factory as alpha_miner
from pm4py.algo.discovery.dfg.adapters.pandas import df_statistics as dfg_util
from pm4py.algo.filtering.common.filtering_constants import CASE_CONCEPT_NAME
from pm4py.algo.filtering.pandas.attributes import attributes_filter
from pm4py.algo.filtering.pandas.auto_filter import auto_filter
from pm4py.algo.filtering.pandas.end_activities import end_activities_filter
from pm4py.algo.filtering.pandas.start_activities import start_activities_filter
from pm4py.algo.simulation.simple.filtering.pandas.versions import filter_topvariants_soundmodel
from pm4py.objects.log.util.xes import DEFAULT_NAME_KEY
from pm4py.objects.log.util.xes import DEFAULT_TIMESTAMP_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ATTRIBUTE_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_CASEID_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_TIMESTAMP_KEY


def apply(df, parameters=None, classic_output=False):
    """
    Gets a simple model out of a Pandas dataframe

    Parameters
    -------------
    df
        Pandas dataframe
    parameters
        Parameters of the algorithm, including:
            maximum_number_activities -> Maximum number of activities to keep
            discovery_algorithm -> Discovery algorithm to use (alpha, inductive)
            desidered_output -> Desidered output of the algorithm (default: Petri)
            include_filtered_df -> Include the filtered dataframe in the output
            include_dfg_frequency -> Include the DFG of frequencies in the output
            include_dfg_performance -> Include the DFG of performance in the output
            include_filtered_dfg_frequency -> Include the filtered DFG of frequencies in the output
            include_filtered_dfg_performance -> Include the filtered DFG of performance in the output
    classic_output
        Determine if the output shall contains directly the objects (e.g. net, initial_marking, final_marking)
        or can return a more detailed dictionary
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

    returned_dictionary = {}

    caseid_glue = parameters[PARAMETER_CONSTANT_CASEID_KEY]
    activity_key = parameters[PARAMETER_CONSTANT_ACTIVITY_KEY]
    timest_key = parameters[PARAMETER_CONSTANT_TIMESTAMP_KEY]

    net = None
    initial_marking = None
    final_marking = None
    bpmn_graph = None

    maximum_number_activities = parameters[
        "maximum_number_activities"] if "maximum_number_activities" in parameters else 20
    discovery_algorithm = parameters["discovery_algorithm"] if "discovery_algorithm" in parameters else "alphaclassic"
    desidered_output = parameters["desidered_output"] if "desidered_output" in parameters else "petri"
    include_filtered_df = parameters["include_filtered_df"] if "include_filtered_df" in parameters else True
    include_dfg_frequency = parameters["include_dfg_frequency"] if "include_dfg_frequency" in parameters else True
    include_dfg_performance = parameters["include_dfg_performance"] if "include_dfg_performance" in parameters else True
    include_filtered_dfg_frequency = parameters[
        "include_filtered_dfg_frequency"] if "include_filtered_dfg_frequency" in parameters else True
    include_filtered_dfg_performance = parameters[
        "include_filtered_dfg_performance"] if "include_filtered_dfg_performance" in parameters else True

    df = attributes_filter.filter_df_keeping_spno_activities(df, activity_key=activity_key,
                                                             max_no_activities=maximum_number_activities)

    filtered_df = None

    if "alpha" in discovery_algorithm:
        filtered_df = start_activities_filter.apply_auto_filter(df, parameters=parameters)
        filtered_df = end_activities_filter.apply_auto_filter(filtered_df, parameters=parameters)
        filtered_df = filter_topvariants_soundmodel.apply(filtered_df, parameters=parameters)
    elif "inductive" in discovery_algorithm:
        filtered_df = auto_filter.apply_auto_filter(df, parameters=parameters)

    [dfg_frequency, dfg_performance] = dfg_util.get_dfg_graph(df, measure="both",
                                                              perf_aggregation_key="mean",
                                                              case_id_glue=caseid_glue,
                                                              activity_key=activity_key,
                                                              timestamp_key=timest_key)

    [filtered_dfg_frequency, filtered_dfg_performance] = dfg_util.get_dfg_graph(filtered_df, measure="both",
                                                                                perf_aggregation_key="mean",
                                                                                case_id_glue=caseid_glue,
                                                                                activity_key=activity_key,
                                                                                timestamp_key=timest_key)

    if "alpha" in discovery_algorithm:
        net, initial_marking, final_marking = alpha_miner.apply_dfg(filtered_dfg_frequency, parameters=parameters)

    if filtered_df is not None and include_filtered_df:
        returned_dictionary["filtered_df"] = filtered_df
    if net is not None and desidered_output == "petri":
        returned_dictionary["net"] = net
    if initial_marking is not None and desidered_output == "petri":
        returned_dictionary["initial_marking"] = initial_marking
    if final_marking is not None and desidered_output == "petri":
        returned_dictionary["final_marking"] = final_marking
    if bpmn_graph is not None and desidered_output == "bpmn":
        returned_dictionary["bpmn_graph"] = bpmn_graph
    if dfg_frequency is not None and include_dfg_frequency:
        returned_dictionary["dfg_frequency"] = dfg_frequency
    if dfg_performance is not None and include_dfg_performance:
        returned_dictionary["dfg_performance"] = dfg_performance
    if filtered_dfg_frequency is not None and include_filtered_dfg_frequency:
        returned_dictionary["filtered_dfg_frequency"] = filtered_dfg_frequency
    if filtered_dfg_performance is not None and include_filtered_dfg_performance:
        returned_dictionary["filtered_dfg_performance"] = filtered_dfg_performance

    if classic_output:
        if net is not None and desidered_output == "petri":
            return net, initial_marking, final_marking

    return returned_dictionary

from pm4py.algo.other.simple.filtering.tracelog.versions import filter_topvariants_soundmodel
from pm4py.algo.filtering.tracelog.attributes import attributes_filter
from pm4py.algo.filtering.tracelog.auto_filter import auto_filter
from pm4py.objects.log.util.xes import DEFAULT_NAME_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ATTRIBUTE_KEY, PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.algo.discovery.alpha import factory as alpha_miner


def apply(log, parameters=None):
    if parameters is None:
        parameters = {}

    returned_dictionary = {}

    net = None
    initial_marking = None
    final_marking = None
    bpmn_graph = None
    dfg_frequency = None
    dfg_performance = None
    filtered_dfg_frequency = None
    filtered_dfg_performance = None

    maximum_number_activities = parameters[
        "maximum_number_activities"] if "maximum_number_activities" in parameters else 20
    discovery_algorithm = parameters["discovery_algorithm"] if "discovery_algorithm" in parameters else "alphaclassic"
    desidered_output = parameters["desidered_output"] if "desidered_output" in parameters else "petri"
    include_filtered_log = parameters["include_filtered_log"] if "include_filtered_log" in parameters else True
    include_dfg_frequency = parameters["include_dfg_frequency"] if "include_dfg_frequency" in parameters else True
    include_dfg_performance = parameters["include_dfg_performance"] if "include_dfg_performance" in parameters else True
    include_filtered_dfg_frequency = parameters[
        "include_filtered_dfg_frequency"] if "include_filtered_dfg_frequency" in parameters else True
    include_filtered_dfg_performance = parameters[
        "include_filtered_dfg_performance"] if "include_filtered_dfg_performance" in parameters else True
    apply_dfg_filtering = parameters["apply_dfg_filtering"] if "apply_dfg_filtering" in parameters else True
    dfg_filtering_threshold = parameters["dfg_filtering_threshold"] if "dfg_filtering_threshold" in parameters else 0.01

    attribute_key = parameters[
        PARAMETER_CONSTANT_ATTRIBUTE_KEY] if PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else DEFAULT_NAME_KEY

    activities_count_dictio = attributes_filter.get_attribute_values(log, attribute_key)
    activities_count_list = []
    for activity in activities_count_dictio:
        activities_count_list.append([activity, activities_count_dictio[activity]])

    activities_count_list = sorted(activities_count_list, key=lambda x: x[1], reverse=True)
    activities_count_list = activities_count_list[:min(len(activities_count_list), maximum_number_activities)]
    activities_keep_list = [x[0] for x in activities_count_list]

    log = attributes_filter.apply(log, activities_keep_list, parameters=parameters)

    if "alpha" in discovery_algorithm:
        filtered_log = filter_topvariants_soundmodel.apply(log, parameters=parameters)
    elif "inductive" in discovery_algorithm:
        filtered_log = auto_filter.apply(log, parameters=parameters)

    if "alpha" in discovery_algorithm:
        net, initial_marking, final_marking = alpha_miner.apply(filtered_log)

    if filtered_log is not None and include_filtered_log:
        returned_dictionary["filtered_log"] = filtered_log
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

    return returned_dictionary

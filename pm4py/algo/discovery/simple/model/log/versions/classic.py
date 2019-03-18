from pm4py.algo.discovery.alpha import factory as alpha_miner
from pm4py.algo.discovery.dfg import factory as dfg_factory
from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.algo.filtering.log.auto_filter import auto_filter
from pm4py.algo.filtering.log.start_activities import start_activities_filter
from pm4py.algo.filtering.log.end_activities import end_activities_filter
from pm4py.algo.discovery.simple.filtering.log.versions import filter_topvariants_soundmodel
from pm4py.objects.log.util import insert_classifier
from pm4py.objects.log.util.xes import DEFAULT_NAME_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ATTRIBUTE_KEY, PARAMETER_CONSTANT_ACTIVITY_KEY
from copy import deepcopy

def apply(log, parameters=None, classic_output=False):
    """
    Gets a simple model out of a log

    Parameters
    -------------
    log
        Trace log
    parameters
        Parameters of the algorithm, including:
            maximum_number_activities -> Maximum number of activities to keep
            discovery_algorithm -> Discovery algorithm to use (alpha, inductive)
            desidered_output -> Desidered output of the algorithm (default: Petri)
            include_filtered_log -> Include the filtered log in the output
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
    include_dfg_performance = parameters["include_dfg_performance"] if "include_dfg_performance" in parameters else False
    include_filtered_dfg_frequency = parameters[
        "include_filtered_dfg_frequency"] if "include_filtered_dfg_frequency" in parameters else True
    include_filtered_dfg_performance = parameters[
        "include_filtered_dfg_performance"] if "include_filtered_dfg_performance" in parameters else False

    if PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters:
        activity_key = parameters[
            PARAMETER_CONSTANT_ATTRIBUTE_KEY] if PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else DEFAULT_NAME_KEY
        parameters[PARAMETER_CONSTANT_ATTRIBUTE_KEY] = activity_key
    else:
        log, activity_key = insert_classifier.search_act_class_attr(log)
        if activity_key is None:
            activity_key = DEFAULT_NAME_KEY
        parameters[PARAMETER_CONSTANT_ATTRIBUTE_KEY] = activity_key

    if PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters:
        parameters[PARAMETER_CONSTANT_ACTIVITY_KEY] = parameters[PARAMETER_CONSTANT_ATTRIBUTE_KEY]

    activities_count_dictio = attributes_filter.get_attribute_values(log, activity_key)
    activities_count_list = []
    for activity in activities_count_dictio:
        activities_count_list.append([activity, activities_count_dictio[activity]])

    activities_count_list = sorted(activities_count_list, key=lambda x: x[1], reverse=True)
    activities_count_list = activities_count_list[:min(len(activities_count_list), maximum_number_activities)]
    activities_keep_list = [x[0] for x in activities_count_list]

    log = attributes_filter.apply(log, activities_keep_list, parameters=parameters)

    filtered_log = None

    if "alpha" in discovery_algorithm:
        #parameters_sa = deepcopy(parameters)
        #parameters_sa["decreasingFactor"] = 1.0
        filtered_log = start_activities_filter.apply_auto_filter(log, parameters=parameters)
        filtered_log = end_activities_filter.apply_auto_filter(filtered_log, parameters=parameters)
        filtered_log = filter_topvariants_soundmodel.apply(filtered_log, parameters=parameters)
    elif "inductive" in discovery_algorithm:
        filtered_log = auto_filter.apply_auto_filter(log, parameters=parameters)

    if include_dfg_frequency:
        dfg_frequency = dfg_factory.apply(log, parameters=parameters, variant="frequency")
    if include_dfg_performance:
        dfg_performance = dfg_factory.apply(log, parameters=parameters, variant="performance")
    if include_filtered_dfg_frequency:
        filtered_dfg_frequency = dfg_factory.apply(filtered_log, parameters=parameters, variant="frequency")
    if include_filtered_dfg_performance:
        filtered_dfg_performance = dfg_factory.apply(filtered_log, parameters=parameters, variant="performance")

    if "alpha" in discovery_algorithm:
        net, initial_marking, final_marking = alpha_miner.apply(filtered_log, parameters=parameters)

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

    if classic_output:
        if net is not None and desidered_output == "petri":
            return net, initial_marking, final_marking

    return returned_dictionary

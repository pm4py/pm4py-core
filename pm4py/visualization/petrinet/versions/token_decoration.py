import pm4py
from pm4py.algo.conformance.tokenreplay import factory as token_replay
from pm4py.algo.filtering.log.variants import variants_filter as variants_module
from pm4py.objects import log as log_lib
from pm4py.visualization.petrinet.common import visualize
from pm4py.visualization.petrinet.util import performance_map

PARAM_ACTIVITY_KEY = pm4py.util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY
PARAM_TIMESTAMP_KEY = pm4py.util.constants.PARAMETER_CONSTANT_TIMESTAMP_KEY

PARAMETERS = [PARAM_ACTIVITY_KEY, PARAM_TIMESTAMP_KEY]


def get_decorations(log, net, initial_marking, final_marking, parameters=None, measure="frequency",
                    ht_perf_method="last"):
    """
    Calculate decorations in order to annotate the Petri net

    Parameters
    -----------
    log
        Trace log
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    parameters
        Parameters associated to the algorithm
    measure
        Measure to represent on the process model (frequency/performance)
    ht_perf_method
        Method to use in order to annotate hidden transitions (performance value could be put on the last possible
        point (last) or in the first possible point (first)

    Returns
    ------------
    decorations
        Decorations to put on the process model
    """
    if parameters is None:
        parameters = {}

    aggregation_measure = None
    if "aggregationMeasure" in parameters:
        aggregation_measure = parameters["aggregationMeasure"]

    activity_key = parameters[
        PARAM_ACTIVITY_KEY] if PARAM_ACTIVITY_KEY in parameters else log_lib.util.xes.DEFAULT_NAME_KEY
    timestamp_key = parameters[PARAM_TIMESTAMP_KEY] if PARAM_TIMESTAMP_KEY in parameters else "time:timestamp"

    parameters_variants = {PARAM_ACTIVITY_KEY: activity_key}
    variants_idx = variants_module.get_variants_from_log_trace_idx(log, parameters=parameters_variants)
    variants = variants_module.convert_variants_trace_idx_to_trace_obj(log, variants_idx)

    parameters_tr = {PARAM_ACTIVITY_KEY: activity_key, "variants": variants}

    # do the replay
    aligned_traces = token_replay.apply(log, net, initial_marking, final_marking, parameters=parameters_tr)

    # apply petri_reduction technique in order to simplify the Petri net
    # net = reduction.apply(net, parameters={"aligned_traces": aligned_traces})

    element_statistics = performance_map.single_element_statistics(log, net, initial_marking,
                                                                   aligned_traces, variants_idx,
                                                                   activity_key=activity_key,
                                                                   timestamp_key=timestamp_key,
                                                                   ht_perf_method=ht_perf_method)

    aggregated_statistics = performance_map.aggregate_statistics(element_statistics, measure=measure,
                                                                 aggregation_measure=aggregation_measure)

    return aggregated_statistics


def apply_frequency(net, initial_marking, final_marking, log=None, aggregated_statistics=None, parameters=None):
    """
    Apply method for Petri net visualization (useful for recall from factory; it calls the graphviz_visualization
    method) adding frequency representation obtained by token replay

    Parameters
    -----------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    log
        (Optional) log
    aggregated_statistics
        Dictionary containing the frequency statistics
    parameters
        Algorithm parameters (including the activity key used during the replay, and the timestamp key)

    Returns
    -----------
    viz
        Graph object
    """
    if aggregated_statistics is None:
        if log is not None:
            aggregated_statistics = get_decorations(log, net, initial_marking, final_marking, parameters=parameters,
                                                    measure="frequency")
    return visualize.apply(net, initial_marking, final_marking, parameters=parameters,
                           decorations=aggregated_statistics)


def apply_performance(net, initial_marking, final_marking, log=None, aggregated_statistics=None, parameters=None):
    """
    Apply method for Petri net visualization (useful for recall from factory; it calls the graphviz_visualization
    method) adding performance representation obtained by token replay

    Parameters
    -----------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    log
        (Optional) log
    aggregated_statistics
        Dictionary containing the frequency statistics
    parameters
        Algorithm parameters (including the activity key used during the replay, and the timestamp key)

    Returns
    -----------
    viz
        Graph object
    """
    if aggregated_statistics is None:
        if log is not None:
            aggregated_statistics = get_decorations(log, net, initial_marking, final_marking, parameters=parameters,
                                                    measure="performance")
    return visualize.apply(net, initial_marking, final_marking, parameters=parameters,
                           decorations=aggregated_statistics)

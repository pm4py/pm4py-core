import pm4py
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
from pm4py.statistics.variants.log import get as variants_get
from pm4py.visualization.petrinet.common import visualize
from pm4py.visualization.petrinet.util import performance_map
from pm4py.util import exec_utils, xes_constants
from pm4py.visualization.petrinet.parameters import Parameters


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

    aggregation_measure = exec_utils.get_param_value(Parameters.AGGREGATION_MEASURE, parameters, None)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)

    variants_idx = variants_get.get_variants_from_log_trace_idx(log, parameters=parameters)
    variants = variants_get.convert_variants_trace_idx_to_trace_obj(log, variants_idx)

    parameters_tr = {token_replay.Variants.TOKEN_REPLAY.value.Parameters.ACTIVITY_KEY: activity_key,
                     token_replay.Variants.TOKEN_REPLAY.value.Parameters.VARIANTS: variants}

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


def apply(net, initial_marking, final_marking, log=None, aggregated_statistics=None, parameters=None):
    """
    Apply method for Petri net visualization (it calls the graphviz_visualization
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

from pm4py.algo.discovery.dfg import factory as dfg_factory
from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.objects.log.util import xes
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.visualization.petrinet.common import visualize
from pm4py.visualization.petrinet.util.vis_trans_shortest_paths import get_decorations_from_dfg_spaths_acticount
from pm4py.visualization.petrinet.util.vis_trans_shortest_paths import get_shortest_paths


def get_decorated_net(net, initial_marking, final_marking, log, parameters=None, variant="frequency"):
    """
    Get a decorated net according to the specified variant (decorate Petri net based on DFG)

    Parameters
    ------------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    log
        Log to use to decorate the Petri net
    parameters
        Algorithm parameters
    variant
        Specify if the decoration should take into account the frequency or the performance

    Returns
    ------------
    gviz
        GraphViz object
    """
    if parameters is None:
        parameters = {}

    aggregation_measure = "mean"

    if "frequency" in variant:
        aggregation_measure = "sum"
    elif "performance" in variant:
        aggregation_measure = "mean"

    if "aggregationMeasure" in parameters:
        aggregation_measure = parameters["aggregationMeasure"]

    activity_key = parameters[
        PARAMETER_CONSTANT_ACTIVITY_KEY] if PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY

    # we find the DFG
    dfg = dfg_factory.apply(log, variant=variant, parameters=parameters)
    # we find shortest paths
    spaths = get_shortest_paths(net)
    # we find the number of activities occurrences in the log
    activities_count = attributes_filter.get_attribute_values(log, activity_key, parameters=parameters)
    aggregated_statistics = get_decorations_from_dfg_spaths_acticount(net, dfg, spaths,
                                                                      activities_count,
                                                                      variant=variant,
                                                                      aggregation_measure=aggregation_measure)

    return visualize.apply(net, initial_marking, final_marking, parameters=parameters,
                           decorations=aggregated_statistics)


def apply_frequency(net, initial_marking, final_marking, log=None, aggregated_statistics=None, parameters=None):
    """
    Apply frequency decoration through greedy algorithm (decorate Petri net based on DFG)

    Parameters
    ------------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    log
        Log to use to decorate the Petri net
    aggregated_statistics
        Dictionary containing the frequency statistics
    parameters
        Algorithm parameters

    Returns
    ------------
    gviz
        GraphViz object
    """
    del aggregated_statistics
    return get_decorated_net(net, initial_marking, final_marking, log, parameters=parameters, variant="frequency")


def apply_performance(net, initial_marking, final_marking, log=None, aggregated_statistics=None, parameters=None):
    """
    Apply performance decoration through greedy algorithm (decorate Petri net based on DFG)

    Parameters
    ------------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    log
        Log to use to decorate the Petri net
    aggregated_statistics
        Dictionary containing the frequency statistics
    parameters
        Algorithm parameters

    Returns
    ------------
    gviz
        GraphViz object
    """
    del aggregated_statistics
    return get_decorated_net(net, initial_marking, final_marking, log, parameters=parameters, variant="performance")

from pm4py.objects.dfg.retrieval import log as log_retrieval
from pm4py.statistics.attributes.log import get as attr_get
from pm4py.util import xes_constants as xes
from pm4py.visualization.petrinet.common import visualize
from pm4py.visualization.petrinet.util.vis_trans_shortest_paths import get_decorations_from_dfg_spaths_acticount
from pm4py.visualization.petrinet.util.vis_trans_shortest_paths import get_shortest_paths
from pm4py.visualization.petrinet.parameters import Parameters
from pm4py.util import exec_utils


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

    aggregation_measure = exec_utils.get_param_value(Parameters.AGGREGATION_MEASURE, parameters,
                                                     "sum" if "frequency" in variant else "mean")

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes.DEFAULT_NAME_KEY)

    # we find the DFG
    if variant == "performance":
        dfg = log_retrieval.performance(log, parameters=parameters)
    else:
        dfg = log_retrieval.native(log, parameters=parameters)
    # we find shortest paths
    spaths = get_shortest_paths(net)
    # we find the number of activities occurrences in the log
    activities_count = attr_get.get_attribute_values(log, activity_key, parameters=parameters)
    aggregated_statistics = get_decorations_from_dfg_spaths_acticount(net, dfg, spaths,
                                                                      activities_count,
                                                                      variant=variant,
                                                                      aggregation_measure=aggregation_measure)

    return visualize.apply(net, initial_marking, final_marking, parameters=parameters,
                           decorations=aggregated_statistics)


def apply(net, initial_marking, final_marking, log=None, aggregated_statistics=None, parameters=None):
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

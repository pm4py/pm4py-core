from pm4py.visualization.petrinet.common import visualize
from pm4py.visualization.petrinet.util import alignments_decoration


def apply(net, initial_marking, final_marking, log=None, aggregated_statistics=None, parameters=None):
    """
    Apply method for Petri net visualization (useful for recall from factory; it calls the
    graphviz_visualization method)

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
        Algorithm parameters

    Returns
    -----------
    viz
        Graph object
    """
    if aggregated_statistics is None and log is not None:
        aggregated_statistics = alignments_decoration.get_alignments_decoration(net, initial_marking, final_marking,
                                                                                log=log)

    return visualize.apply(net, initial_marking, final_marking, parameters=parameters,
                           decorations=aggregated_statistics)

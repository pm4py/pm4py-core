from pm4py.visualization.transition_system.util import visualize_graphviz
from pm4py.visualization.transition_system.parameters import Parameters


def apply(tsys, parameters=None):
    """
    Get visualization of a Transition System

    Parameters
    -----------
    tsys
        Transition system
    parameters
        Optional parameters of the algorithm

    Returns
    ----------
    gviz
        Graph visualization
    """

    gviz = visualize_graphviz.visualize(tsys, parameters=parameters)
    return gviz

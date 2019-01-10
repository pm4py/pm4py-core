import pm4py


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

    gviz = pm4py.visualization.transition_system.util.visualize_graphviz.visualize(tsys, parameters=parameters)
    return gviz

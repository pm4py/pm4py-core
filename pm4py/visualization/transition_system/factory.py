from pm4py.visualization.transition_system.versions import view_based

VIEW_BASED = "view_based"

VERSIONS = {VIEW_BASED: view_based.apply}

def apply(tsys, parameters=None, variant="view_based"):
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
    return VERSIONS[variant](tsys, parameters=parameters)
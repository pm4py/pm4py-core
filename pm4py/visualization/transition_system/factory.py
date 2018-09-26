from pm4py.visualization.transition_system.versions import view_based
from pm4py.visualization.common.save import *
from pm4py.visualization.common.gview import *

VIEW_BASED = "view_based"
WO_DECORATION = "wo_decoration"
FREQUENCY_DECORATION = "frequency"
PERFORMANCE_DECORATION = "performance"
FREQUENCY_GREEDY = "frequency_greedy"
PERFORMANCE_GREEDY = "performance_greedy"

VERSIONS = {VIEW_BASED: view_based.apply, WO_DECORATION: view_based.apply, FREQUENCY_DECORATION: view_based.apply, PERFORMANCE_DECORATION: view_based.apply, FREQUENCY_GREEDY: view_based.apply, PERFORMANCE_GREEDY: view_based.apply}

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
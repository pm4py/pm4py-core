from pm4py.visualization.common import gview
from pm4py.visualization.common import save as gsave
from pm4py.visualization.transition_system.versions import view_based

VIEW_BASED = "view_based"
WO_DECORATION = "wo_decoration"
FREQUENCY_DECORATION = "frequency"
PERFORMANCE_DECORATION = "performance"
FREQUENCY_GREEDY = "frequency_greedy"
PERFORMANCE_GREEDY = "performance_greedy"

VERSIONS = {VIEW_BASED: view_based.apply, WO_DECORATION: view_based.apply, FREQUENCY_DECORATION: view_based.apply,
            PERFORMANCE_DECORATION: view_based.apply, FREQUENCY_GREEDY: view_based.apply,
            PERFORMANCE_GREEDY: view_based.apply}


def save(gviz, output_file_path):
    """
    Save the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    output_file_path
        Path where the GraphViz output should be saved
    """
    gsave.save(gviz, output_file_path)


def view(gviz):
    """
    View the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    """
    return gview.view(gviz)


def apply(tsys, parameters=None, variant="view_based"):
    """
    Get visualization of a Transition System

    Parameters
    -----------
    tsys
        Transition system
    parameters
        Optional parameters of the algorithm
    variant
        Variant of the algorithm to use, including:
            view_based

    Returns
    ----------
    gviz
        Graph visualization
    """
    return VERSIONS[variant](tsys, parameters=parameters)

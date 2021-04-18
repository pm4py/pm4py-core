from pm4py.visualization.transition_system.util import visualize_graphviz
from enum import Enum


class Parameters(Enum):
    FORMAT = "format"
    SHOW_LABELS = "show_labels"
    SHOW_NAMES = "show_names"
    FORCE_NAMES = "force_names"
    FILLCOLORS = "fillcolors"
    FONT_SIZE = "font_size"


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

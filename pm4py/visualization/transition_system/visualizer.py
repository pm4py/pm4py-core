from pm4py.visualization.common import gview
from pm4py.visualization.common import save as gsave
from pm4py.visualization.transition_system.versions import view_based
from enum import Enum
from pm4py.util import exec_utils


class Variants(Enum):
    VIEW_BASED = view_based


DEFAULT_VARIANT = Variants.VIEW_BASED


def apply(tsys, parameters=None, variant=DEFAULT_VARIANT):
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
            - Variants.VIEW_BASED

    Returns
    ----------
    gviz
        Graph visualization
    """
    return exec_utils.get_variant(variant).apply(tsys, parameters=parameters)


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


def matplotlib_view(gviz):
    """
    Views the diagram using Matplotlib

    Parameters
    ---------------
    gviz
        Graphviz
    """

    return gview.matplotlib_view(gviz)

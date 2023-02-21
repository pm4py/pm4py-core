from pm4py.visualization.common import gview
from pm4py.visualization.common import save as gsave
from pm4py.visualization.transition_system.variants import view_based, trans_frequency
from enum import Enum
from pm4py.util import exec_utils
from pm4py.visualization.common.gview import serialize, serialize_dot
from typing import Optional, Dict, Any, Union, Tuple
from pm4py.objects.transition_system.obj import TransitionSystem
import graphviz


class Variants(Enum):
    VIEW_BASED = view_based
    TRANS_FREQUENCY = trans_frequency


DEFAULT_VARIANT = Variants.VIEW_BASED


def apply(tsys: TransitionSystem, parameters: Optional[Dict[Any, Any]] = None, variant=DEFAULT_VARIANT) -> graphviz.Digraph:
    """
    Get visualization of a Transition System

    Parameters
    -----------
    tsys
        Transition system
    parameters
        Parameters of the algorithm
    variant
        Variant of the algorithm to use, including:
            - Variants.VIEW_BASED

    Returns
    ----------
    gviz
        Graph visualization
    """
    return exec_utils.get_variant(variant).apply(tsys, parameters=parameters)


def save(gviz: graphviz.Digraph, output_file_path: str, parameters=None):
    """
    Save the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    output_file_path
        Path where the GraphViz output should be saved
    """
    gsave.save(gviz, output_file_path, parameters=parameters)


def view(gviz: graphviz.Digraph, parameters=None):
    """
    View the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    """
    return gview.view(gviz, parameters=parameters)


def matplotlib_view(gviz: graphviz.Digraph, parameters=None):
    """
    Views the diagram using Matplotlib

    Parameters
    ---------------
    gviz
        Graphviz
    """

    return gview.matplotlib_view(gviz, parameters=parameters)

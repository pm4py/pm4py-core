from graphviz import Digraph
from enum import Enum
from pm4py.util import exec_utils
from pm4py.visualization.ocel.ocdfg.variants import classic
from typing import Optional, Dict, Any
from pm4py.visualization.common import gview
from pm4py.visualization.common import save as gsave


class Variants(Enum):
    CLASSIC = classic


def apply(ocdfg: Dict[str, Any], variant=Variants.CLASSIC, parameters: Optional[Dict[Any, Any]] = None) -> Digraph:
    """
    Visualizes an OC-DFG using one of the provided visualizations.

    Parameters
    ----------------
    ocdfg
        Object-centric directly-follows graph
    variant
        Available variants. Possible values:
        - Variants.CLASSIC
    parameters
        Variant-specific parameters

    Returns
    ----------------
    viz
        Graphviz DiGraph
    """
    return exec_utils.get_variant(variant).apply(ocdfg, parameters)


def save(gviz: Digraph, output_file_path: str, parameters=None):
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


def view(gviz: Digraph, parameters=None):
    """
    View the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    """
    return gview.view(gviz, parameters=parameters)


def matplotlib_view(gviz: Digraph, parameters=None):
    """
    Views the diagram using Matplotlib

    Parameters
    ---------------
    gviz
        Graphviz
    """

    return gview.matplotlib_view(gviz, parameters=parameters)

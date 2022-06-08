from graphviz import Digraph
from enum import Enum
from pm4py.util import exec_utils
from pm4py.visualization.ocel.object_graph.variants import graphviz
from typing import Optional, Dict, Any, Set, Tuple
from pm4py.visualization.common import gview
from pm4py.visualization.common import save as gsave
from pm4py.objects.ocel.obj import OCEL


class Variants(Enum):
    GRAPHVIZ = graphviz


def apply(ocel: OCEL, graph: Set[Tuple[str, str]], variant=Variants.GRAPHVIZ, parameters: Optional[Dict[Any, Any]] = None) -> Digraph:
    """
    Visualizes an object graph

    Parameters
    -----------------
    ocel
        Object-centric event log
    graph
        Object graph
    variant
        Variant of the visualization to use, possible values:
        - Variants.GRAPHVIZ
    parameters
        Variant-specific parameters

    Returns
    -----------------
    gviz
        Graphviz object
    """
    return exec_utils.get_variant(variant).apply(ocel, graph, parameters=parameters)


def save(gviz: Digraph, output_file_path: str):
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


def view(gviz: Digraph):
    """
    View the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    """
    return gview.view(gviz)


def matplotlib_view(gviz: Digraph):
    """
    Views the diagram using Matplotlib

    Parameters
    ---------------
    gviz
        Graphviz
    """

    return gview.matplotlib_view(gviz)

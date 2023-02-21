from enum import Enum
from typing import Optional, Dict, Any

from graphviz import Graph

from pm4py.objects.trie.obj import Trie
from pm4py.util import exec_utils
from pm4py.visualization.common import gview
from pm4py.visualization.common import save as gsave
from pm4py.visualization.trie.variants import classic


class Variants(Enum):
    CLASSIC = classic


def apply(trie: Trie, variant=Variants.CLASSIC, parameters: Optional[Dict[Any, Any]] = None) -> Graph:
    """
    Represents the trie

    Parameters
    -----------------
    trie
        Trie
    variant
        Variant of the visualization, possible values:
        - Variants.CLASSIC => graphviz visualization
    parameters
        Parameters, including:
        - Parameters.FORMAT: the format of the visualization

    Returns
    -----------------
    graph
        Representation of the trie
    """
    return exec_utils.get_variant(variant).apply(trie, parameters=parameters)


def save(gviz: Graph, output_file_path: str, parameters=None):
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


def view(gviz: Graph, parameters=None):
    """
    View the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    """
    return gview.view(gviz, parameters=parameters)


def matplotlib_view(gviz: Graph, parameters=None):
    """
    Views the diagram using Matplotlib

    Parameters
    ---------------
    gviz
        Graphviz
    """

    return gview.matplotlib_view(gviz, parameters=parameters)

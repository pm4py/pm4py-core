from graphviz import Digraph
from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any
from pm4py.visualization.common import gview
from pm4py.visualization.common import save as gsave
from pm4py.visualization.ocel.interleavings.variants import graphviz
import pandas as pd


class Variants(Enum):
    GRAPHVIZ = graphviz


def apply(dataframe1: pd.DataFrame, dataframe2: pd.DataFrame, interleavings: pd.DataFrame, variant=Variants.GRAPHVIZ,
          parameters: Optional[Dict[Any, Any]] = None) -> Digraph:
    """
    Visualizes the interleavings discovered between two different processes.
    We suppose to provide both event logs, and the discovered interleavings.
    The visualization includes the DFG of both processes, along with the arcs discovered between them.
    Both frequency and performance visualization are available.

    Parameters
    --------------------
    dataframe1
        Dataframe of the first process
    dataframe2
        Dataframe of the second process
    interleavings
        Interleavings between the two considered processes
    variant
        Variant of the visualizer to apply, possible values: Variants.GRAPHVIZ
    parameters
        Variant-specific parameters

    Returns
    ----------------
    digraph
        Graphviz Digraph
    """
    return exec_utils.get_variant(variant).apply(dataframe1, dataframe2, interleavings, parameters=parameters)


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

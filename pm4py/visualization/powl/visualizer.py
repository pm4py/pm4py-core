from pm4py.visualization.common import gview
from pm4py.visualization.common import save as gsave
from pm4py.visualization.powl.variants import basic
from pm4py.visualization.powl.variants import net
from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any
from pm4py.objects.powl.obj import POWL
import graphviz


class POWLVisualizationVariants(Enum):
    BASIC = basic
    NET = net


DEFAULT_VARIANT = POWLVisualizationVariants.BASIC


def apply(powl: POWL, parameters: Optional[Dict[Any, Any]] = None, variant=DEFAULT_VARIANT, frequency_tags=True)\
        -> graphviz.Graph:
    """
    Method for POWL model representation

    Parameters
    -----------
    powl
        POWL model
    parameters
        Possible parameters of the algorithm:
            Parameters.FORMAT -> Format of the image (PDF, PNG, SVG; default PNG)
    variant
        Variant of the algorithm to use:
            - POWLVisualizationVariants.BASIC (default)
            - POWLVisualizationVariants.NET: BPMN-like visualization with decision gates
    frequency_tags
        Simplify the visualization using frequency tags

    Returns
    -----------
    gviz
        GraphViz object
    """
    if frequency_tags:
        powl = powl.simplify_using_frequent_transitions()

    return exec_utils.get_variant(variant).apply(powl, parameters=parameters)


def save(gviz: graphviz.Graph, output_file_path: str):
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
    return ""


def view(gviz: graphviz.Graph):
    """
    View the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    """
    return gview.view(gviz)


def matplotlib_view(gviz: graphviz.Graph):
    """
    Views the diagram using Matplotlib

    Parameters
    ---------------
    gviz
        Graphviz
    """

    return gview.matplotlib_view(gviz)

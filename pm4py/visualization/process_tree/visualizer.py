from pm4py.visualization.common import gview
from pm4py.visualization.common import save as gsave
from pm4py.visualization.process_tree.variants import wo_decoration, symbolic, frequency_annotation
from enum import Enum
from pm4py.util import exec_utils
from pm4py.visualization.common.gview import serialize, serialize_dot
from typing import Optional, Dict, Any
from pm4py.objects.process_tree.obj import ProcessTree
import graphviz


class Variants(Enum):
    WO_DECORATION = wo_decoration
    SYMBOLIC = symbolic
    FREQUENCY_ANNOTATION = frequency_annotation


DEFAULT_VARIANT = Variants.WO_DECORATION


def apply(tree0: ProcessTree, parameters: Optional[Dict[Any, Any]] = None, variant=DEFAULT_VARIANT) -> graphviz.Graph:
    """
    Method for Process Tree representation

    Parameters
    -----------
    tree
        Process tree
    parameters
        Possible parameters of the algorithm:
            Parameters.FORMAT -> Format of the image (PDF, PNG, SVG; default PNG)
            Parameters.BGCOLOR -> Background color to be used (i.e., 'white' or 'transparent')
            Parameters.RANKDIR -> Direction of the graph ("LR" for left-to-right; "TB" for top-to-bottom)
    variant
        Variant of the algorithm to use:
            - Variants.WO_DECORATION

    Returns
    -----------
    gviz
        GraphViz object
    """
    return exec_utils.get_variant(variant).apply(tree0, parameters=parameters)


def save(gviz: graphviz.Graph, output_file_path: str, parameters=None):
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


def view(gviz: graphviz.Graph, parameters=None):
    """
    View the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    """
    return gview.view(gviz, parameters=parameters)


def matplotlib_view(gviz: graphviz.Graph, parameters=None):
    """
    Views the diagram using Matplotlib

    Parameters
    ---------------
    gviz
        Graphviz
    """

    return gview.matplotlib_view(gviz, parameters=parameters)

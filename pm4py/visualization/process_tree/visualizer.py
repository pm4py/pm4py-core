from pm4py.visualization.common import gview
from pm4py.visualization.common import save as gsave
from pm4py.visualization.process_tree.versions import wo_decoration
from enum import Enum
from pm4py.util import exec_utils


class Variants(Enum):
    WO_DECORATION = wo_decoration


DEFAULT_VARIANT = Variants.WO_DECORATION


def apply(tree0, parameters=None, variant=DEFAULT_VARIANT):
    """
    Method for Process Tree representation

    Parameters
    -----------
    tree
        Process tree
    parameters
        Possible parameters of the algorithm:
            Parameters.FORMAT -> Format of the image (PDF, PNG, SVG; default PNG)
    variant
        Variant of the algorithm to use:
            - Variants.WO_DECORATION

    Returns
    -----------
    gviz
        GraphViz object
    """
    return exec_utils.get_variant(variant).apply(tree0, parameters=parameters)


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

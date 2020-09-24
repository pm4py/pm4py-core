from pm4py.visualization.footprints.variants import comparison, single
from enum import Enum
from pm4py.util import exec_utils
from pm4py.visualization.common import gview
from pm4py.visualization.common import save as gsave


class Variants(Enum):
    COMPARISON = comparison
    SINGLE = single


def apply(*args, variant=None, parameters=None):
    """
    Visualize a footprints table or a comparison between footprints
    tables

    Parameters
    ---------------
    args
        Arguments:
        - A single footprint table
        - Two footprints table (first one associated to the log, second
        one associated to the model)
    parameters
        Parameters of the algorithm, including:
            - Parameters.FORMAT => Format of the visualization

    Returns
    ---------------
    gviz
        Graphviz object
    """
    if parameters is None:
        parameters = {}

    if variant is None:
        if len(args) == 1:
            variant = Variants.SINGLE
        else:
            variant = Variants.COMPARISON

    if variant in [Variants.SINGLE]:
        return exec_utils.get_variant(variant).apply(args[0], parameters=parameters)
    elif variant in [Variants.COMPARISON]:
        return exec_utils.get_variant(variant).apply(args[0], args[1], parameters=parameters)


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

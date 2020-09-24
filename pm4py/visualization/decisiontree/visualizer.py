from pm4py.visualization.decisiontree.versions import classic
from pm4py.visualization.common import gview
from pm4py.visualization.common import save as gsave
from enum import Enum
from pm4py.util import exec_utils


class Variants(Enum):
    CLASSIC = classic


DEFAULT_VARIANT = Variants.CLASSIC


def apply(clf, feature_names, classes, parameters=None, variant=DEFAULT_VARIANT):
    """
    Method to apply the visualization of the decision tree

    Parameters
    ------------
    clf
        Decision tree
    feature_names
        Names of the provided features
    classes
        Names of the target classes
    parameters
        Possible parameters of the algorithm, including:
            Parameters.FORMAT -> Image format (pdf, svg, png ...)
    variant
        Variant of the algorithm:
            - Variants.CLASSIC

    Returns
    ------------
    gviz
        GraphViz object
    """
    return exec_utils.get_variant(variant).apply(clf, feature_names, classes, parameters=parameters)


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

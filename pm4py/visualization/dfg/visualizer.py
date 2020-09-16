from pm4py.visualization.common import gview
from pm4py.visualization.common import save as gsave
from pm4py.visualization.dfg.variants import frequency, performance
from enum import Enum
from pm4py.util import exec_utils


class Variants(Enum):
    FREQUENCY = frequency
    PERFORMANCE = performance


DEFAULT_VARIANT = Variants.FREQUENCY


def apply(dfg, log=None, activities_count=None, parameters=None, variant=DEFAULT_VARIANT):
    return exec_utils.get_variant(variant).apply(dfg, log=log, activities_count=activities_count, parameters=parameters)


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

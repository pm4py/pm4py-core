from pm4py.visualization.align_table.versions import classic
from pm4py.visualization.common import gview
from pm4py.visualization.common import save as gsave
from enum import Enum
from pm4py.util import exec_utils


class Variants(Enum):
    CLASSIC = classic


DEFAULT_VARIANT = Variants.CLASSIC


def apply(log, aligned_traces, variant=DEFAULT_VARIANT, parameters=None):
    """
    Gets the alignment table visualization from the alignments output

    Parameters
    -------------
    log
        Event log
    aligned_traces
        Aligned traces
    variant
        Variant of the algorithm to apply, possible values:
            - Variants.CLASSIC
    parameters
        Parameters of the algorithm

    Returns
    -------------
    gviz
        Graphviz object
    """
    return exec_utils.get_variant(variant).apply(log, aligned_traces, parameters=parameters)


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

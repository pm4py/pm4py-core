from pm4py.visualization.align_table.versions import classic
from pm4py.visualization.common import gview
from pm4py.visualization.common import save as gsave

CLASSIC = "classic"

VERSIONS = {CLASSIC: classic.apply}


def apply(log, aligned_traces, variant=CLASSIC, parameters=None):
    return VERSIONS[variant](log, aligned_traces, parameters=parameters)


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

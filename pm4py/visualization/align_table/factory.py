import deprecation

from pm4py.visualization.align_table.versions import classic
from pm4py.visualization.common import gview
from pm4py.visualization.common import save as gsave

CLASSIC = "classic"

VERSIONS = {CLASSIC: classic.apply}

@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Use visualizer module instead.')
def apply(log, aligned_traces, variant=CLASSIC, parameters=None):
    """
    Gets the alignment table visualization from the alignments output

    Parameters
    -------------
    log
        Event log
    aligned_traces
        Aligned traces
    variant
        Variant of the algorithm to apply, possible values: classic
    parameters
        Parameters of the algorithm

    Returns
    -------------
    gviz
        Graphviz object
    """
    return VERSIONS[variant](log, aligned_traces, parameters=parameters)

@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Use visualizer module instead.')
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

@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Use visualizer module instead.')
def view(gviz):
    """
    View the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    """
    return gview.view(gviz)

import deprecation

from pm4py.visualization.common import gview
from pm4py.visualization.common import save as gsave
from pm4py.visualization.dfg.versions import simple_visualize

FREQUENCY = "frequency"
PERFORMANCE = "performance"
FREQUENCY_GREEDY = "frequency_greedy"
PERFORMANCE_GREEDY = "performance_greedy"

VERSIONS = {FREQUENCY: simple_visualize.apply_frequency, PERFORMANCE: simple_visualize.apply_performance,
            FREQUENCY_GREEDY: simple_visualize.apply_frequency, PERFORMANCE_GREEDY: simple_visualize.apply_performance}

@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Use visualizer module instead.')
def apply(dfg, log=None, activities_count=None, parameters=None, variant="frequency"):
    return VERSIONS[variant](dfg, log=log, activities_count=activities_count, parameters=parameters)

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

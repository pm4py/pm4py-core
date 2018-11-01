from pm4py.visualization.common import gview
from pm4py.visualization.common import save as gsave
from pm4py.visualization.petrinet.versions import wo_decoration, token_decoration, greedy_decoration

WO_DECORATION = "wo_decoration"
FREQUENCY_DECORATION = "frequency"
PERFORMANCE_DECORATION = "performance"
FREQUENCY_GREEDY = "frequency_greedy"
PERFORMANCE_GREEDY = "performance_greedy"

VERSIONS = {WO_DECORATION: wo_decoration.apply, FREQUENCY_DECORATION: token_decoration.apply_frequency,
            PERFORMANCE_DECORATION: token_decoration.apply_performance,
            FREQUENCY_GREEDY: greedy_decoration.apply_frequency,
            PERFORMANCE_GREEDY: greedy_decoration.apply_performance}


def apply(net, initial_marking=None, final_marking=None, log=None, aggregated_statistics=None, parameters=None,
          variant="wo_decoration"):
    return VERSIONS[variant](net, initial_marking, final_marking, log=log, aggregated_statistics=aggregated_statistics,
                             parameters=parameters)


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

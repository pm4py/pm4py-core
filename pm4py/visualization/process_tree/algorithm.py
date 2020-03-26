from pm4py.visualization.common import gview
from pm4py.visualization.common import save as gsave
from pm4py.visualization.process_tree.versions import wo_decoration
from pm4py.objects.process_tree import util
from copy import deepcopy


WO_DECORATION = "wo_decoration"
FREQUENCY_DECORATION = "frequency"
PERFORMANCE_DECORATION = "performance"
FREQUENCY_GREEDY = "frequency_greedy"
PERFORMANCE_GREEDY = "performance_greedy"

VERSIONS = {WO_DECORATION: wo_decoration.apply, FREQUENCY_DECORATION: wo_decoration.apply,
            PERFORMANCE_DECORATION: wo_decoration.apply, FREQUENCY_GREEDY: wo_decoration.apply,
            PERFORMANCE_GREEDY: wo_decoration.apply}


def apply(tree0, parameters=None, variant="wo_decoration"):
    """
    Factory method for Process Tree representation

    Parameters
    -----------
    tree
        Process tree
    parameters
        Possible parameters of the algorithm:
            circle_width -> Width of the circles containing the operators
            circle_font_size -> Font size associated to the operators
            box_width -> Width of the box associated to the transitions
            box_font_size -> Font size associated to the transitions boxes
            format -> Format of the image (PDF, PNG, SVG; default PNG)
    variant
        Variant of the algorithm to use

    Returns
    -----------
    gviz
        GraphViz object
    """
    # since the process tree object needs to be sorted in the visualization, make a deepcopy of it before
    # proceeding
    tree = deepcopy(tree0)
    util.tree_sort(tree)
    return VERSIONS[variant](tree, parameters=parameters)


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

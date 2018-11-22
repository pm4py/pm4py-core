from pm4py.visualization.decisiontree.versions import classic
from pm4py.visualization.common import gview
from pm4py.visualization.common import save as gsave


CLASSIC = "classic"

VERSIONS = {CLASSIC: classic.apply}


def apply(clf, feature_names, classes, parameters=None, variant="classic"):
    """
    Factory method to apply the visualization of the decision tree

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
            format -> Image format (pdf, svg, png ...)
    variant
        Variant of the algorithm

    Returns
    ------------
    gviz
        GraphViz object
    """
    return VERSIONS[variant](clf, feature_names, classes, parameters=parameters)


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
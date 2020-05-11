import graphviz
import tempfile
from pm4py.visualization.parameters import Parameters
from pm4py.util import exec_utils


def apply(clf, feature_names, classes, parameters=None):
    """
    Apply the visualization of the decision tree

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

    Returns
    ------------
    gviz
        GraphViz object
    """
    from sklearn import tree

    if parameters is None:
        parameters = {}

    format = exec_utils.get_param_value(Parameters.FORMAT, parameters, "png")
    filename = tempfile.NamedTemporaryFile(suffix='.gv')

    dot_data = tree.export_graphviz(clf, out_file=None,
                                    feature_names=feature_names,
                                    class_names=classes,
                                    filled=True, rounded=True,
                                    special_characters=True)
    gviz = graphviz.Source(dot_data)
    gviz.format = format
    gviz.filename = filename.name

    return gviz

from sklearn import tree
import graphviz
import tempfile


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
            format -> Image format (pdf, svg, png ...)

    Returns
    ------------
    gviz
        GraphViz object
    """
    if parameters is None:
        parameters = {}

    format = parameters["format"] if "format" in parameters else "png"
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

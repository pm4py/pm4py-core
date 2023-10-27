import tempfile
from pm4py.util import exec_utils
from enum import Enum
from sklearn import tree
from typing import Optional, Dict, Any, Union, List
import graphviz


class Parameters(Enum):
    FORMAT = "format"


def apply(clf: tree.DecisionTreeClassifier, feature_names: List[str], classes: List[str], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> graphviz.Source:
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
    if parameters is None:
        parameters = {}

    format = exec_utils.get_param_value(Parameters.FORMAT, parameters, "png")
    filename = tempfile.NamedTemporaryFile(suffix='.gv')
    filename.close()

    dot_data = tree.export_graphviz(clf, out_file=None,
                                    feature_names=feature_names,
                                    class_names=classes,
                                    filled=True, rounded=True,
                                    special_characters=True)
    gviz = graphviz.Source(dot_data)
    gviz.format = format
    gviz.filename = filename.name

    return gviz

'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
import tempfile
from pm4py.util import exec_utils
from enum import Enum
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import export_graphviz
from typing import Optional, Dict, Any, Union, List
import graphviz


class Parameters(Enum):
    FORMAT = "format"


def apply(clf: DecisionTreeClassifier, feature_names: List[str], classes: List[str], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> graphviz.Source:
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

    dot_data = export_graphviz(clf, out_file=None,
                                    feature_names=feature_names,
                                    class_names=classes,
                                    filled=True, rounded=True,
                                    special_characters=True)
    gviz = graphviz.Source(dot_data)
    gviz.format = format
    gviz.filename = filename.name

    return gviz

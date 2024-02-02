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
from pm4py.visualization.decisiontree.variants import classic
from pm4py.visualization.common import gview
from pm4py.visualization.common import save as gsave
from enum import Enum
from pm4py.util import exec_utils
from pm4py.visualization.common.gview import serialize, serialize_dot
from sklearn.tree import DecisionTreeClassifier
from typing import Optional, Dict, Any, List
import graphviz


class Variants(Enum):
    CLASSIC = classic


DEFAULT_VARIANT = Variants.CLASSIC


def apply(clf: DecisionTreeClassifier, feature_names: List[str], classes: List[str], parameters: Optional[Dict[Any, Any]] = None, variant=DEFAULT_VARIANT) -> graphviz.Source:
    """
    Method to apply the visualization of the decision tree

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
    variant
        Variant of the algorithm:
            - Variants.CLASSIC

    Returns
    ------------
    gviz
        GraphViz object
    """
    return exec_utils.get_variant(variant).apply(clf, feature_names, classes, parameters=parameters)


def save(gviz: graphviz.Source, output_file_path: str, parameters=None):
    """
    Save the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    output_file_path
        Path where the GraphViz output should be saved
    """
    gsave.save(gviz, output_file_path, parameters=parameters)


def view(gviz: graphviz.Source, parameters=None):
    """
    View the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    """
    return gview.view(gviz, parameters=parameters)


def matplotlib_view(gviz: graphviz.Source, parameters=None):
    """
    Views the diagram using Matplotlib

    Parameters
    ---------------
    gviz
        Graphviz
    """

    return gview.matplotlib_view(gviz, parameters=parameters)

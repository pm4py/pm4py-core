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
from pm4py.visualization.common import gview
from pm4py.visualization.common import save as gsave
from pm4py.visualization.process_tree.variants import wo_decoration, symbolic, frequency_annotation
from enum import Enum
from pm4py.util import exec_utils
from pm4py.visualization.common.gview import serialize, serialize_dot
from typing import Optional, Dict, Any
from pm4py.objects.process_tree.obj import ProcessTree
import graphviz


class Variants(Enum):
    WO_DECORATION = wo_decoration
    SYMBOLIC = symbolic
    FREQUENCY_ANNOTATION = frequency_annotation


DEFAULT_VARIANT = Variants.WO_DECORATION


def apply(tree0: ProcessTree, parameters: Optional[Dict[Any, Any]] = None, variant=DEFAULT_VARIANT) -> graphviz.Graph:
    """
    Method for Process Tree representation

    Parameters
    -----------
    tree
        Process tree
    parameters
        Possible parameters of the algorithm:
            Parameters.FORMAT -> Format of the image (PDF, PNG, SVG; default PNG)
            Parameters.BGCOLOR -> Background color to be used (i.e., 'white' or 'transparent')
            Parameters.RANKDIR -> Direction of the graph ("LR" for left-to-right; "TB" for top-to-bottom)
    variant
        Variant of the algorithm to use:
            - Variants.WO_DECORATION

    Returns
    -----------
    gviz
        GraphViz object
    """
    return exec_utils.get_variant(variant).apply(tree0, parameters=parameters)


def save(gviz: graphviz.Graph, output_file_path: str, parameters=None):
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
    return ""


def view(gviz: graphviz.Graph, parameters=None):
    """
    View the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    """
    return gview.view(gviz, parameters=parameters)


def matplotlib_view(gviz: graphviz.Graph, parameters=None):
    """
    Views the diagram using Matplotlib

    Parameters
    ---------------
    gviz
        Graphviz
    """

    return gview.matplotlib_view(gviz, parameters=parameters)

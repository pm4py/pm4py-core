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
from pm4py.visualization.bpmn.variants import classic
from pm4py.util import exec_utils
from enum import Enum
from pm4py.visualization.common import gview
from pm4py.visualization.common import save as gsave
from pm4py.visualization.common.gview import serialize, serialize_dot
from typing import Optional, Dict, Any, Union, Tuple
from pm4py.objects.bpmn.obj import BPMN
from pm4py.util import typing
import graphviz


class Variants(Enum):
    CLASSIC = classic


DEFAULT_VARIANT = Variants.CLASSIC


def apply(bpmn_graph: BPMN, variant=DEFAULT_VARIANT, parameters: Optional[Dict[Any, Any]] = None) -> graphviz.Digraph:
    """
    Visualize a BPMN graph

    Parameters
    -------------
    bpmn_graph
        BPMN graph
    variant
        Variant of the visualization, possible values:
         - Variants.CLASSIC
    parameters
        Version-specific parameters

    Returns
    ------------
    gviz
        Graphviz representation
    """
    return exec_utils.get_variant(variant).apply(bpmn_graph, parameters=parameters)


def save(gviz: graphviz.Digraph, output_file_path: str):
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


def view(gviz: graphviz.Digraph):
    """
    View the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    """
    return gview.view(gviz)


def matplotlib_view(gviz: graphviz.Digraph):
    """
    Views the diagram using Matplotlib

    Parameters
    ---------------
    gviz
        Graphviz
    """

    return gview.matplotlib_view(gviz)

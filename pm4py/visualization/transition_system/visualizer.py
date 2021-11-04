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
from pm4py.visualization.transition_system.variants import view_based
from enum import Enum
from pm4py.util import exec_utils
from pm4py.visualization.common.gview import serialize, serialize_dot
from typing import Optional, Dict, Any, Union, Tuple
from pm4py.objects.transition_system.obj import TransitionSystem
import graphviz


class Variants(Enum):
    VIEW_BASED = view_based


DEFAULT_VARIANT = Variants.VIEW_BASED


def apply(tsys: TransitionSystem, parameters: Optional[Dict[Any, Any]] = None, variant=DEFAULT_VARIANT) -> graphviz.Digraph:
    """
    Get visualization of a Transition System

    Parameters
    -----------
    tsys
        Transition system
    parameters
        Parameters of the algorithm
    variant
        Variant of the algorithm to use, including:
            - Variants.VIEW_BASED

    Returns
    ----------
    gviz
        Graph visualization
    """
    return exec_utils.get_variant(variant).apply(tsys, parameters=parameters)


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

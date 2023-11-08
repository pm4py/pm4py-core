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
from pm4py.visualization.transition_system.util import visualize_graphviz
from enum import Enum
from typing import Optional, Dict, Any, Union
from pm4py.objects.transition_system.obj import TransitionSystem
import graphviz


class Parameters(Enum):
    FORMAT = "format"
    SHOW_LABELS = "show_labels"
    SHOW_NAMES = "show_names"
    FORCE_NAMES = "force_names"
    FILLCOLORS = "fillcolors"
    FONT_SIZE = "font_size"


def apply(tsys: TransitionSystem, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> graphviz.Digraph:
    """
    Get visualization of a Transition System

    Parameters
    -----------
    tsys
        Transition system
    parameters
        Optional parameters of the algorithm

    Returns
    ----------
    gviz
        Graph visualization
    """

    gviz = visualize_graphviz.visualize(tsys, parameters=parameters)
    return gviz

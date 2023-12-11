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
from graphviz import Digraph
from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any
from pm4py.visualization.common import gview
from pm4py.visualization.common import save as gsave
from pm4py.visualization.networkx.variants import digraph
import networkx as nx


class Variants(Enum):
    DIGRAPH = digraph


def apply(G: nx.DiGraph, variant=Variants.DIGRAPH,
          parameters: Optional[Dict[Any, Any]] = None) -> Digraph:
    """
    Creates a Graphviz Digraph from a NetworkX DiGraph object.

    Parameters
    ---------------
    G
        NetworkX DiGraph
    parameters
        Variant-specific parameters

    Returns
    --------------
    digraph
        Graphviz DiGraph object
    """
    return exec_utils.get_variant(variant).apply(G, parameters=parameters)


def save(gviz: Digraph, output_file_path: str, parameters=None):
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


def view(gviz: Digraph, parameters=None):
    """
    View the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    """
    return gview.view(gviz, parameters=parameters)


def matplotlib_view(gviz: Digraph, parameters=None):
    """
    Views the diagram using Matplotlib

    Parameters
    ---------------
    gviz
        Graphviz
    """

    return gview.matplotlib_view(gviz, parameters=parameters)

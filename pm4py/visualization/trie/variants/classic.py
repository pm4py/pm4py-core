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
from enum import Enum
from typing import Optional, Dict, Any, Union

from graphviz import Graph

from pm4py.objects.trie.obj import Trie
from pm4py.util import exec_utils


class Parameters(Enum):
    FORMAT = "format"
    BGCOLOR = "bgcolor"


def draw_recursive(trie_node: Trie, parent: Union[str, None], gviz: Graph):
    """
    Draws recursively the specified trie node

    Parameters
    --------------
    trie_node
        Node of the trie
    parent
        Parent node in the graph (expressed as a string)
    gviz
        Graphviz object
    """
    node_id = str(id(trie_node))
    if trie_node.label is not None:
        gviz.node(node_id, label=trie_node.label, shape="box")
    if parent is not None:
        gviz.edge(parent, node_id)
    for child in trie_node.children:
        draw_recursive(child, node_id if trie_node.label is not None else None, gviz)


def apply(trie: Trie, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Graph:
    """
    Represents the trie

    Parameters
    -----------------
    trie
        Trie
    parameters
        Parameters, including:
        - Parameters.FORMAT: the format of the visualization

    Returns
    -----------------
    graph
        Representation of the trie
    """
    if parameters is None:
        parameters = {}

    image_format = exec_utils.get_param_value(Parameters.FORMAT, parameters, "png")
    bgcolor = exec_utils.get_param_value(Parameters.BGCOLOR, parameters, "transparent")

    filename = tempfile.NamedTemporaryFile(suffix='.gv')
    viz = Graph("pt", filename=filename.name, engine='dot', graph_attr={'bgcolor': bgcolor})
    viz.attr('node', shape='ellipse', fixedsize='false')

    draw_recursive(trie, None, viz)

    viz.attr(overlap='false')
    viz.attr(splines='false')
    viz.attr(rankdir='LR')
    viz.format = image_format

    return viz

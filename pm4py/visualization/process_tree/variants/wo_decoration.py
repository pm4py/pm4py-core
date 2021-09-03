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
import uuid
from copy import deepcopy
from enum import Enum

from graphviz import Graph

from pm4py.objects.process_tree.utils import generic
from pm4py.util import exec_utils
from typing import Optional, Dict, Any, Union, Tuple
from pm4py.objects.process_tree.obj import ProcessTree
import graphviz


class Parameters(Enum):
    FORMAT = "format"
    COLOR_MAP = "color_map"
    ENABLE_DEEPCOPY = "enable_deepcopy"
    FONT_SIZE = "font_size"
    BGCOLOR = "bgcolor"


# maps the operators to the ProM strings
operators_mapping = {"->": "seq", "X": "xor", "+": "and", "*": "xor loop", "O": "or"}


def get_color(node, color_map):
    """
    Gets a color for a node from the color map

    Parameters
    --------------
    node
        Node
    color_map
        Color map
    """
    if node in color_map:
        return color_map[node]
    return "black"


def repr_tree(tree, viz, current_node, rec_depth, color_map, parameters):
    """
    Represent a subtree on the GraphViz object

    Parameters
    -----------
    tree
        Current subtree
    viz
        GraphViz object
    current_node
        Father node of the current subtree
    rec_depth
        Reached recursion depth
    color_map
        Color map
    parameters
        Possible parameters of the algorithm.

    Returns
    -----------
    gviz
        (partial) GraphViz object
    """
    if tree.operator is None:
        this_trans_id = str(uuid.uuid4())
        if tree.label is None:
            viz.node(this_trans_id, "tau", style='filled', fillcolor='black', shape='point', width="0.075")
        else:
            node_color = get_color(tree, color_map)
            viz.node(this_trans_id, str(tree), color=node_color, fontcolor=node_color)
        viz.edge(current_node, this_trans_id, dirType='none')
    else:
        op_node_identifier = str(uuid.uuid4())
        node_color = get_color(tree, color_map)
        viz.node(op_node_identifier, operators_mapping[str(tree.operator)], color=node_color, fontcolor=node_color)
        viz.edge(current_node, op_node_identifier, dirType='none')
        viz = repr_tree(tree, viz, op_node_identifier, rec_depth + 1, color_map, parameters)

    return viz


def repr_tree_2(tree, viz, color_map, parameters):
    font_size = exec_utils.get_param_value(Parameters.FONT_SIZE, parameters, 15)
    font_size = str(font_size)

    this_node_id = str(id(tree))

    if tree.operator is None:
        if tree.label is None:
            viz.node(this_node_id, "tau", style='filled', fillcolor='black', shape='point', width="0.075", fontsize=font_size)
        else:
            node_color = get_color(tree, color_map)
            viz.node(this_node_id, str(tree), color=node_color, fontcolor=node_color, fontsize=font_size)
    else:
        node_color = get_color(tree, color_map)
        viz.node(this_node_id, operators_mapping[str(tree.operator)], color=node_color, fontcolor=node_color, fontsize=font_size)

        for child in tree.children:
            repr_tree_2(child, viz, color_map, parameters)

    if tree.parent is not None:
        viz.edge(str(id(tree.parent)), this_node_id, dirType='none')


def apply(tree: ProcessTree, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> graphviz.Graph:
    """
    Obtain a Process Tree representation through GraphViz

    Parameters
    -----------
    tree
        Process tree
    parameters
        Possible parameters of the algorithm

    Returns
    -----------
    gviz
        GraphViz object
    """
    if parameters is None:
        parameters = {}

    filename = tempfile.NamedTemporaryFile(suffix='.gv')

    bgcolor = exec_utils.get_param_value(Parameters.BGCOLOR, parameters, "transparent")

    viz = Graph("pt", filename=filename.name, engine='dot', graph_attr={'bgcolor': bgcolor})
    viz.attr('node', shape='ellipse', fixedsize='false')

    image_format = exec_utils.get_param_value(Parameters.FORMAT, parameters, "png")
    color_map = exec_utils.get_param_value(Parameters.COLOR_MAP, parameters, {})

    enable_deepcopy = exec_utils.get_param_value(Parameters.ENABLE_DEEPCOPY, parameters, True)

    if enable_deepcopy:
        # since the process tree object needs to be sorted in the visualization, make a deepcopy of it before
        # proceeding
        tree = deepcopy(tree)
        generic.tree_sort(tree)

    repr_tree_2(tree, viz, color_map, parameters)

    viz.attr(overlap='false')
    viz.attr(splines='false')
    viz.format = image_format

    return viz

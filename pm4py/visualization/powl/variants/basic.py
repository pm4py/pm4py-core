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
from graphviz import Digraph
from pm4py.objects.powl.constants import SILENT_TRANSITION_LABEL
from pm4py.objects.process_tree.obj import Operator
from pm4py.util import exec_utils, constants
from typing import Optional, Dict, Any, Union
from pm4py.objects.powl.obj import POWL, Transition, SilentTransition, StrictPartialOrder, OperatorPOWL

COLOR_ORDER = "red"
COLOR_OPERATOR = "black"
COLOR_LEAF = "blue"
NODE_IN_PO = False


class Parameters(Enum):
    FORMAT = "format"
    COLOR_MAP = "color_map"
    ENABLE_DEEPCOPY = "enable_deepcopy"
    FONT_SIZE = "font_size"
    BGCOLOR = "bgcolor"
    RANKDIR = "rankdir"


def apply(powl: POWL, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Digraph:
    """
    Obtain a POWL model representation through GraphViz

    Parameters
    -----------
    powl
        POWL model
    parameters
        Possible parameters of the algorithm

    Returns
    -----------
    gviz
        GraphViz Digraph
    """
    if parameters is None:
        parameters = {}

    image_format = exec_utils.get_param_value(Parameters.FORMAT, parameters, "png")
    color_map = exec_utils.get_param_value(Parameters.COLOR_MAP, parameters, {})
    bgcolor = exec_utils.get_param_value(Parameters.BGCOLOR, parameters, constants.DEFAULT_BGCOLOR)
    rankdir = exec_utils.get_param_value(Parameters.RANKDIR, parameters, "TB")

    filename = tempfile.NamedTemporaryFile(suffix='.gv')
    filename.close()

    viz = Digraph("powl", filename=filename.name, engine='dot', graph_attr={'bgcolor': bgcolor})
    viz.graph_attr['rankdir'] = rankdir

    viz.attr('node', shape='ellipse', fixedsize='false')
    viz.attr(nodesep='1')
    viz.attr(ranksep='1')
    viz.attr(compound='true')
    viz.attr(overlap='scale')
    viz.attr(splines='true')

    repr_powl(powl, viz, color_map, parameters)
    viz.format = image_format.replace("html", "plain-ext")

    return viz


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


def get_id_base(powl):
    if isinstance(powl, Transition):
        return str(id(powl))
    if isinstance(powl, OperatorPOWL):
        return str(id(powl))
    if isinstance(powl, StrictPartialOrder):
        for node in powl.children:
            return get_id_base(node)


def get_id(powl):
    if isinstance(powl, Transition):
        return str(id(powl))
    if isinstance(powl, OperatorPOWL):
        return "clusterINVIS_" + str(id(powl))
    if isinstance(powl, StrictPartialOrder):
        return "cluster_" + str(id(powl))


def add_operator_edge(vis, current_node_id, child, directory='none', style=""):
    child_id = get_id(child)
    if child_id.startswith("cluster_"):
        vis.edge(current_node_id, get_id_base(child), dir=directory, lhead=child_id, style=style)
    else:
        vis.edge(current_node_id, get_id_base(child), dir=directory, style=style)


def add_order_edge(block, child_1, child_2, directory='forward', color=COLOR_ORDER, style=""):
    child_id_1 = get_id(child_1)
    child_id_2 = get_id(child_2)
    if child_id_1.startswith("cluster_"):
        if child_id_2.startswith("cluster_"):
            block.edge(get_id_base(child_1), get_id_base(child_2), dir=directory, color=color, style=style,
                       ltail=child_id_1, lhead=child_id_2)
        else:
            block.edge(get_id_base(child_1), get_id_base(child_2), dir=directory, color=color, style=style,
                       ltail=child_id_1)
    else:
        if child_id_2.startswith("cluster_"):
            block.edge(get_id_base(child_1), get_id_base(child_2), dir=directory, color=color, style=style,
                       lhead=child_id_2)
        else:
            block.edge(get_id_base(child_1), get_id_base(child_2), dir=directory, color=color, style=style)


def repr_powl(powl, viz, color_map, parameters):
    font_size = exec_utils.get_param_value(Parameters.FONT_SIZE, parameters, 25)
    font_size = str(font_size)
    this_node_id = str(id(powl))

    if isinstance(powl, Transition):
        if isinstance(powl, SilentTransition):
            viz.node(this_node_id, SILENT_TRANSITION_LABEL, style='filled', fillcolor='black', shape='point',
                     width="0.2", fontsize=font_size)
        else:
            viz.node(this_node_id, str(powl.label), color=COLOR_LEAF, fontcolor=COLOR_LEAF, fontsize=font_size)

    elif isinstance(powl, StrictPartialOrder):
        transitive_reduction = powl.order.get_transitive_reduction()
        with viz.subgraph(name=get_id(powl)) as block:
            block.attr(style="")
            for child in powl.children:
                repr_powl(child, block, color_map, parameters)
            for child in powl.children:
                for child2 in powl.children:
                    if transitive_reduction.is_edge(child, child2):
                        add_order_edge(block, child, child2)

    elif isinstance(powl, OperatorPOWL):
        with viz.subgraph(name=get_id(powl)) as block:
            block.attr(style="invis")
            node_color = COLOR_OPERATOR
            block.node(this_node_id, powl.operator.__repr__(), color=node_color, fontcolor=node_color,
                       fontsize=font_size)
            if powl.operator == Operator.LOOP:
                do = powl.children[0]
                redo = powl.children[1]
                repr_powl(do, block, color_map, parameters)
                add_operator_edge(block, this_node_id, do)
                repr_powl(redo, block, color_map, parameters)
                add_operator_edge(block, this_node_id, redo, style="dashed")
            else:
                for child in powl.children:
                    repr_powl(child, block, color_map, parameters)
                    add_operator_edge(block, this_node_id, child)

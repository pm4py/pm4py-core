import tempfile
import uuid
from graphviz import Digraph
from pm4py.objects.process_tree import pt_operator
from pm4py.util import exec_utils
from pm4py.objects.process_tree import util
from copy import deepcopy
from enum import Enum


class Parameters(Enum):
    FORMAT = "format"
    COLOR_MAP = "color_map"
    ENABLE_DEEPCOPY = "enable_deepcopy"


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
    for child in tree.children:
        if child.operator is None:
            viz.attr('node', shape='box', fixedsize='true', width="2.5",
                     fontsize="8")
            this_trans_id = str(uuid.uuid4())
            if child.label is None:
                viz.node(this_trans_id, "tau", style='filled', fillcolor='black')
            else:
                node_color = get_color(child, color_map)
                viz.node(this_trans_id, str(child), color=node_color, fontcolor=node_color)
            viz.edge(current_node, this_trans_id)
        else:
            condition_wo_operator = child.operator == pt_operator.Operator.XOR and len(
                child.children) == 1 and child.children[0].operator is None
            if condition_wo_operator:
                childchild = child.children[0]
                viz.attr('node', shape='box', fixedsize='true', width="2.5",
                         fontsize="8")
                this_trans_id = str(uuid.uuid4())
                if childchild.label is None:
                    viz.node(this_trans_id, str(childchild), style='filled', fillcolor='black')
                else:
                    node_color = get_color(childchild, color_map)
                    viz.node(this_trans_id, str(childchild), color=node_color, fontcolor=node_color)
                viz.edge(current_node, this_trans_id)
            else:
                viz.attr('node', shape='circle', fixedsize='true', width="0.6",
                         fontsize="14")
                op_node_identifier = str(uuid.uuid4())
                node_color = get_color(child, color_map)
                viz.node(op_node_identifier, str(child.operator), color=node_color, fontcolor=node_color)
                viz.edge(current_node, op_node_identifier)
                viz = repr_tree(child, viz, op_node_identifier, rec_depth + 1, color_map, parameters)
    return viz


def apply(tree, parameters=None):
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
    viz = Digraph("pt", filename=filename.name, engine='dot', graph_attr={'bgcolor': 'transparent'})
    image_format = exec_utils.get_param_value(Parameters.FORMAT, parameters, "png")
    color_map = exec_utils.get_param_value(Parameters.COLOR_MAP, parameters, {})
    node_color = get_color(tree, color_map)

    enable_deepcopy = exec_utils.get_param_value(Parameters.ENABLE_DEEPCOPY, parameters, True)

    if enable_deepcopy:
        # since the process tree object needs to be sorted in the visualization, make a deepcopy of it before
        # proceeding
        tree = deepcopy(tree)
        util.tree_sort(tree)

    # add first operator
    if tree.operator:
        viz.attr('node', shape='circle', fixedsize='true', width="0.6",
                 fontsize="14")
        op_node_identifier = str(uuid.uuid4())
        viz.node(op_node_identifier, str(tree.operator), color=node_color, fontcolor=node_color)

        viz = repr_tree(tree, viz, op_node_identifier, 0, color_map, parameters)
    else:
        viz.attr('node', shape='box', fixedsize='true', width="2.5",
                 fontsize="8")
        this_trans_id = str(uuid.uuid4())
        if tree.label is None:
            viz.node(this_trans_id, "tau", style='filled', fillcolor='black')
        else:
            viz.node(this_trans_id, str(tree), color=node_color, fontcolor=node_color)

    viz.attr(overlap='false')
    viz.attr(fontsize='11')
    viz.format = image_format

    return viz

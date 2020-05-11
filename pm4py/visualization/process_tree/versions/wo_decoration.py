import tempfile
import uuid
from graphviz import Digraph
from pm4py.objects.process_tree import pt_operator
from enum import Enum
from pm4py.util import exec_utils
from pm4py.visualization.parameters import Parameters


def repr_tree(tree, viz, current_node, rec_depth, parameters):
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
                viz.node(this_trans_id, str(child))
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
                    viz.node(this_trans_id, str(childchild))
                viz.edge(current_node, this_trans_id)
            else:
                viz.attr('node', shape='circle', fixedsize='true', width="0.6",
                         fontsize="14")
                op_node_identifier = str(uuid.uuid4())
                viz.node(op_node_identifier, str(child.operator))
                viz.edge(current_node, op_node_identifier)
                viz = repr_tree(child, viz, op_node_identifier, rec_depth + 1, parameters)
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

    # add first operator
    if tree.operator:
        viz.attr('node', shape='circle', fixedsize='true', width="0.6",
                 fontsize="14")
        op_node_identifier = str(uuid.uuid4())
        viz.node(op_node_identifier, str(tree.operator))

        viz = repr_tree(tree, viz, op_node_identifier, 0, parameters)
    else:
        viz.attr('node', shape='box', fixedsize='true', width="2.5",
                 fontsize="8")
        this_trans_id = str(uuid.uuid4())
        if tree.label is None:
            viz.node(this_trans_id, "tau", style='filled', fillcolor='black')
        else:
            viz.node(this_trans_id, str(tree))

    viz.attr(overlap='false')
    viz.attr(fontsize='11')
    viz.format = image_format

    return viz

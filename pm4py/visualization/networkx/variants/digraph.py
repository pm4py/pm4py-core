from enum import Enum
from pm4py.util import exec_utils, constants
from typing import Optional, Dict, Any
import graphviz
import tempfile
import uuid
import networkx as nx


class Parameters(Enum):
    FORMAT = "format"
    BGCOLOR = "bgcolor"
    RANKDIR = "rankdir"
    INCLUDE_NODE_ATTRIBUTES = "include_node_attributes"
    INCLUDE_EDGE_ATTRIBUTES = "include_edge_attributes"


def apply(G: nx.DiGraph, parameters: Optional[Dict[Any, Any]] = None) -> graphviz.Digraph:
    """
    Creates a Graphviz Digraph from a NetworkX DiGraph object.

    Parameters
    ---------------
    G
        NetworkX DiGraph
    parameters
        Parameters of the visualization, including:
        - Parameters.FORMAT => format of the visualization (.png, .svg)
        - Parameters.BGCOLOR => background color of the visualization (transparent, white)
        - Parameters.RANKDIR => direction of the graph (LR or TB)
        - Parameters.INCLUDE_NODE_ATTRIBUTES => includes the node attributes in the node's label in the representation
        - Parameters.INCLUDE_EDGE_ATTRIBUTES => includes the edge attributes in the edge's label in the representation

    Returns
    --------------
    digraph
        Graphviz DiGraph object
    """
    if parameters is None:
        parameters = {}

    format = exec_utils.get_param_value(Parameters.FORMAT, parameters, constants.DEFAULT_FORMAT_GVIZ_VIEW)
    bgcolor = exec_utils.get_param_value(Parameters.BGCOLOR, parameters, constants.DEFAULT_BGCOLOR)
    rankdir = exec_utils.get_param_value(Parameters.RANKDIR, parameters, "LR")

    include_node_attributes = exec_utils.get_param_value(Parameters.INCLUDE_NODE_ATTRIBUTES, parameters, True)
    include_edge_attributes = exec_utils.get_param_value(Parameters.INCLUDE_EDGE_ATTRIBUTES, parameters, True)

    filename = tempfile.NamedTemporaryFile(suffix='.gv')
    viz = graphviz.Digraph("networkx_digraph", filename=filename.name, engine='dot', graph_attr={'bgcolor': bgcolor})

    nodes_dict = {}
    for node in G.nodes:
        node_id = str(uuid.uuid4())
        nodes_dict[node] = node_id
        label = str(node)

        if include_node_attributes and G.nodes[node]:
            label += "\n" + str(G.nodes[node]).replace(", ", ",\n")

        viz.node(node_id, label=label, shape="box")

    for edge in G.edges:
        label = " "
        if include_edge_attributes and G.edges[edge]:
            label = str(G.edges[edge]).replace(", ", ",\n")

        viz.edge(nodes_dict[edge[0]], nodes_dict[edge[1]], label=label)

    viz.attr(rankdir=rankdir)
    viz.format = format.replace("html", "plain-ext")

    return viz

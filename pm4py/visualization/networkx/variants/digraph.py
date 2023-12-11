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

    Minimum viable example:

        import pm4py
        from pm4py.visualization.networkx import visualizer as nx_to_gv_vis

        log = pm4py.read_xes("../tests/input_data/running-example.xes")
        # gets an 'event graph' where events, cases and their relationships
        # are represented in a graph (NetworkX DiGraph)
        event_graph = pm4py.convert_log_to_networkx(log)

        # visualize the NX DiGraph using Graphviz
        gviz = nx_to_gv_vis.apply(event_graph, parameters={"format": "svg"})
        nx_to_gv_vis.view(gviz)


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

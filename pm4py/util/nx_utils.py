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
import networkx as nx
from enum import Enum
from typing import Optional, Dict, Any
from pm4py.util import exec_utils, constants
import importlib.util
from copy import copy


class Parameters(Enum):
    SHOW_PROGRESS_BAR = "show_progress_bar"


def get_default_nx_environment():
    return nx


DEFAULT_NX_ENVIRONMENT = get_default_nx_environment()


def Graph(*args, **kwargs):
    return DEFAULT_NX_ENVIRONMENT.Graph(*args, **kwargs)


def DiGraph(*args, **kwargs):
    return DEFAULT_NX_ENVIRONMENT.DiGraph(*args, **kwargs)


def MultiGraph(*args, **kwargs):
    return DEFAULT_NX_ENVIRONMENT.MultiGraph(*args, **kwargs)


def MultiDiGraph(*args, **kwargs):
    return DEFAULT_NX_ENVIRONMENT.MultiDiGraph(*args, **kwargs)


def ancestors(*args, **kwargs):
    return DEFAULT_NX_ENVIRONMENT.ancestors(*args, **kwargs)


def descendants(*args, **kwargs):
    return DEFAULT_NX_ENVIRONMENT.descendants(*args, **kwargs)


def connected_components(*args, **kwargs):
    return DEFAULT_NX_ENVIRONMENT.connected_components(*args, **kwargs)


def bfs_tree(*args, **kwargs):
    return DEFAULT_NX_ENVIRONMENT.bfs_tree(*args, **kwargs)


def contracted_nodes(*args, **kwargs):
    return DEFAULT_NX_ENVIRONMENT.contracted_nodes(*args, **kwargs)


def shortest_path(*args, **kwargs):
    return DEFAULT_NX_ENVIRONMENT.shortest_path(*args, **kwargs)


def strongly_connected_components(*args, **kwargs):
    return DEFAULT_NX_ENVIRONMENT.strongly_connected_components(*args, **kwargs)


def has_path(*args, **kwargs):
    return DEFAULT_NX_ENVIRONMENT.has_path(*args, **kwargs)


def is_strongly_connected(*args, **kwargs):
    return DEFAULT_NX_ENVIRONMENT.is_strongly_connected(*args, **kwargs)


def all_pairs_shortest_path(*args, **kwargs):
    return DEFAULT_NX_ENVIRONMENT.all_pairs_shortest_path(*args, **kwargs)


def all_pairs_dijkstra(*args, **kwargs):
    return DEFAULT_NX_ENVIRONMENT.all_pairs_dijkstra(*args, **kwargs)


def find_cliques(*args, **kwargs):
    return DEFAULT_NX_ENVIRONMENT.find_cliques(*args, **kwargs)


def degree_centrality(*args, **kwargs):
    return DEFAULT_NX_ENVIRONMENT.degree_centrality(*args, **kwargs)


def greedy_modularity_communities(*args, **kwargs):
    return DEFAULT_NX_ENVIRONMENT.algorithms.community.greedy_modularity_communities(*args, **kwargs)


def maximum_flow_value(*args, **kwargs):
    return DEFAULT_NX_ENVIRONMENT.maximum_flow_value(*args, **kwargs)


def minimum_weight_full_matching(*args, **kwargs):
    return DEFAULT_NX_ENVIRONMENT.bipartite.minimum_weight_full_matching(*args, **kwargs)


def Edmonds(*args, **kwargs):
    return DEFAULT_NX_ENVIRONMENT.algorithms.tree.Edmonds(*args, **kwargs)


def __format_attrs(attributes0: Dict[str, Any]) -> Dict[str, Any]:
    """
    Internal method to format properties.
    """
    attributes = {}

    keys = list(attributes0.keys())

    for k0 in keys:
        v = attributes0[k0]
        t = str(type(v)).lower()

        k = k0
        if "time" in t:
            v = v.isoformat()
            attributes[k] = v
        elif "float" in t or "double" in t:
            attributes[k] = v
        elif "str" in t:
            attributes[k] = v
        else:
            attributes[k] = str(v)

    return attributes


def neo4j_upload(nx_graph: nx.DiGraph, session, clean_db: bool = True, parameters: Optional[Dict[Any, Any]] = None):
    """
    Uploads a NetworkX DiGraph obtained from a traditional/object-centric event log to a Neo4J session

    Parameters
    ---------------
    nx_graph
        NetworkX graph
    session
        Neo4J session
    clean_db
        Cleans the database before uploading
    parameters
        Other optional parameters of the method, including:
        - Parameters.SHOW_PROGRESS_BAR => shows the percentage of nodes/edges uploaded to Neo4J
    """
    if parameters is None:
        parameters = {}

    show_progress_bar = exec_utils.get_param_value(Parameters.SHOW_PROGRESS_BAR, parameters,
                                                   constants.SHOW_PROGRESS_BAR)

    if clean_db:
        session.run("MATCH (n) DETACH DELETE n")

    nodes = list(nx_graph.nodes)
    nodes_progress = None
    edges = list(nx_graph.edges)
    edges_progress = None

    if importlib.util.find_spec("tqdm") and show_progress_bar:
        from tqdm.auto import tqdm
        nodes_progress = tqdm(total=len(nodes), desc="uploading nodes, completed :: ")

    for node_id in nodes:
        node_attrs = __format_attrs(nx_graph.nodes[node_id]['attr'])
        node_type = node_attrs["type"]

        command = "CREATE (n:" + node_type + " {id: $id})\nSET n += $properties"

        session.run(command, id=node_id, properties=node_attrs)

        if nodes_progress is not None:
            nodes_progress.update()

    if nodes_progress is not None:
        nodes_progress.close()

    if importlib.util.find_spec("tqdm") and show_progress_bar:
        from tqdm.auto import tqdm
        edges_progress = tqdm(total=len(edges), desc="uploading edges, completed :: ")

    for edge_id in edges:
        edge_attr = __format_attrs(nx_graph.edges[edge_id]['attr'])
        edge_type = edge_attr["type"]

        command = "MATCH (a {id: $id1}), (b {id: $id2})\nCREATE (a)-[r:" + edge_type + " $props]->(b)"

        session.run(command, id1=edge_id[0], id2=edge_id[1], props=edge_attr, edge_type=edge_type)

        if edges_progress is not None:
            edges_progress.update()

    if edges_progress is not None:
        edges_progress.close()


def neo4j_download(session, parameters: Optional[Dict[Any, Any]] = None) -> nx.DiGraph:
    """
    Downloads a NetworkX DiGraph starting from a Neo4J database.

    Parameters
    --------------
    session
        Neo4J session
    parameters
        Optional parameters of the method.

    Returns
    --------------
    nx_graph
        NetworkX DiGraph
    """
    if parameters is None:
        parameters = {}

    from pm4py.util import dt_parsing
    date_parser = dt_parsing.parser.get()

    nodes = session.run("MATCH (n) RETURN n")
    nodes = [dict(node["n"]) for node in nodes]

    edges = session.run("MATCH (n)-[r]->(m) RETURN n, r, m")
    edges = [(edge["n"]["id"], edge["m"]["id"], dict(edge["r"])) for edge in edges]

    nx_graph = DiGraph()

    for n in nodes:
        node_id = n["id"]
        node_props = copy(n)
        del node_props["id"]

        for k in ["ocel:timestamp", "time:timestamp"]:
            if k in node_props:
                node_props[k] = date_parser.apply(node_props[k])

        nx_graph.add_node(node_id, attr=node_props)

    for e in edges:
        nx_graph.add_edge(e[0], e[1], attr=e[2])

    return nx_graph


def nx_to_ocel(nx_graph: nx.DiGraph, parameters: Optional[Dict[Any, Any]] = None):
    """
    Transforms a NetworkX DiGraph representing an OCEL to a proper OCEL.

    Parameters
    ----------------
    nx_graph
        NetworkX DiGraph
    parameters
        Optional parameters of the method

    Returns
    ----------------
    ocel
        Object-centric event log
    """
    if parameters is None:
        parameters = {}

    from pm4py.util import pandas_utils

    events = []
    objects = []
    relations = []
    o2o = []
    object_changes = []

    events_activity = {}
    events_timestamp = {}
    object_types = {}

    for node_id in nx_graph.nodes:
        node_attrs = nx_graph.nodes[node_id]['attr']
        node_type = node_attrs['type']

        if node_type == 'EVENT':
            activity = node_attrs['ocel:activity']
            timestamp = node_attrs['ocel:timestamp']
            events_activity[node_id] = activity
            events_timestamp[node_id] = timestamp
            events.append(node_attrs)
        elif node_type == 'OBJECT':
            object_type = node_attrs['ocel:type']
            object_types[node_id] = object_type
            objects.append(node_attrs)
        elif node_type == 'CHANGE':
            object_changes.append(node_attrs)

    for edge_id in nx_graph.edges:
        source = edge_id[0]
        target = edge_id[1]
        edge_attrs = nx_graph.edges[edge_id]['attr']
        edge_type = edge_attrs['type']
        qualifier = edge_attrs['qualifier'] if 'qualifier' in edge_attrs else ''

        if edge_type == 'E2O':
            activity = events_activity[source]
            timestamp = events_timestamp[source]
            object_type = object_types[target]
            relations.append(
                {"ocel:eid": source, "ocel:oid": target, "ocel:activity": activity, "ocel:timestamp": timestamp,
                 "ocel:type": object_type, "ocel:qualifier": qualifier})
        elif edge_type == 'O2O':
            o2o.append({"ocel:oid": source, "ocel:oid_2": target, "ocel:qualifier": qualifier})

    events = pandas_utils.instantiate_dataframe(events)
    objects = pandas_utils.instantiate_dataframe(objects)
    relations = pandas_utils.instantiate_dataframe(relations)
    o2o = pandas_utils.instantiate_dataframe(o2o) if o2o else None
    object_changes = pandas_utils.instantiate_dataframe(object_changes) if object_changes else None

    internal_index = "@@index"
    events = pandas_utils.insert_index(events, internal_index, reset_index=False, copy_dataframe=False)
    relations = pandas_utils.insert_index(relations, internal_index, reset_index=False, copy_dataframe=False)

    events = events.sort_values(["ocel:timestamp", internal_index])
    relations = relations.sort_values(["ocel:timestamp", internal_index])

    del events[internal_index]
    del relations[internal_index]

    del events["type"]
    del objects["type"]

    if object_changes is not None:
        del object_changes["type"]

    from pm4py.objects.ocel.obj import OCEL

    return OCEL(events, objects, relations, o2o=o2o, object_changes=object_changes)


def nx_to_event_log(nx_graph: nx.DiGraph, parameters: Optional[Dict[Any, Any]] = None):
    """
    Transforms a NetworkX DiGraph representing a traditional event log to a proper event log.

    Parameters
    ----------------
    nx_graph
        NetworkX DiGraph
    parameters
        Optional parameters of the method

    Returns
    ----------------
    event_log
        Traditional event log.
    """
    if parameters is None:
        parameters = {}

    from pm4py.objects.log.obj import EventLog, Trace, Event
    from pm4py.objects.log.util import sorting

    log = EventLog()

    case_nodes = [(k, v["attr"]) for k, v in nx_graph.nodes.items() if v["attr"]["type"] == "CASE"]
    event_nodes = [(k, v["attr"]) for k, v in nx_graph.nodes.items() if v["attr"]["type"] == "EVENT"]

    cases = {}
    for i in range(len(case_nodes)):
        case_attrs = copy(case_nodes[i][1])
        del case_attrs["type"]
        trace = Trace(attributes=case_attrs)
        cases[case_nodes[i][0]] = trace
        log.append(trace)

    events = {}
    for i in range(len(event_nodes)):
        event_attrs = copy(event_nodes[i][1])
        del event_attrs["type"]
        events[event_nodes[i][0]] = Event(event_attrs)

    for edge_id, edge_attrs in nx_graph.edges.items():
        edge_attrs = edge_attrs["attr"]
        edge_type = edge_attrs["type"]

        if edge_type == "BELONGS_TO":
            cases[edge_id[1]].append(events[edge_id[0]])

    log = sorting.sort_timestamp(log, "time:timestamp")

    return log

from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any
from pm4py.algo.transformation.ocel.graphs import object_interaction_graph


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    Adds for each object the centrality degree as feature

    Parameters
    -----------------
    ocel
        OCEL
    parameters
        Parameters of the algorithm

    Returns
    -----------------
    data
        Values of the added features
    feature_names
        Names of the added features
    """
    if parameters is None:
        parameters = {}

    import networkx as nx

    ordered_objects = list(ocel.objects[ocel.object_id_column])
    g0 = object_interaction_graph.apply(ocel, parameters=parameters)
    g = nx.Graph()
    for edge in g0:
        g.add_edge(edge[0], edge[1])

    centrality = nx.degree_centrality(g)

    data = []
    feature_names = ["@@object_degree_centrality"]

    for obj in ordered_objects:
        if obj in centrality:
            data.append([centrality[obj]])
        else:
            data.append([0])

    return data, feature_names

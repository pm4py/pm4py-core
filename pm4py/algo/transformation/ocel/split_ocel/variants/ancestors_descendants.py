from enum import Enum

import networkx as nx

from pm4py.util import exec_utils
from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any, Collection
import sys

class Parameters(Enum):
    OBJECT_TYPE = "object_type"
    MAX_OBJS = "max_objs"


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None) -> Collection[OCEL]:
    """
    Provided an object-centric event log and the specification of an object type,
    splits the OCEL in one OCEL per object of the given object type,
    which is the original OCEL filtered on the current object plus its ascendants and descendants

    Parameters
    ---------------
    ocel
        Object-centric event log
    parameters
        Parameters of the algorithm, including:
        - Parameters.OBJECT_TYPE => the object type to consider when applying the algorithm

    Returns
    ---------------
    lst_ocels
        List of OCELs with the aforementioned possibilities
    """
    if parameters is None:
        parameters = {}

    object_type = exec_utils.get_param_value(Parameters.OBJECT_TYPE, parameters, None)
    if object_type is None:
        raise Exception("the object type should be provided as parameter")
    max_objs = exec_utils.get_param_value(Parameters.MAX_OBJS, parameters, sys.maxsize)

    import pm4py
    interaction_graph = pm4py.discover_objects_graph(ocel, "object_interaction")

    objects_start = ocel.relations.groupby(ocel.object_id_column)[ocel.event_timestamp].first().to_dict()
    objects = set(ocel.objects[ocel.objects[ocel.object_type_column] == object_type][ocel.object_id_column].unique())

    G = nx.DiGraph()
    for obj in objects:
        G.add_node(obj)
    for edge in interaction_graph:
        if objects_start[edge[0]] < objects_start[edge[1]]:
            G.add_edge(edge[0], edge[1])
        elif objects_start[edge[0]] <= objects_start[edge[1]] and edge[0] in objects:
            G.add_edge(edge[0], edge[1])
        elif objects_start[edge[0]] > objects_start[edge[1]]:
            G.add_edge(edge[1], edge[0])
        elif objects_start[edge[0]] >= objects_start[edge[1]] and edge[1] in objects:
            G.add_edge(edge[1], edge[0])

    lst = []

    for index, obj in enumerate(objects):
        if index >= max_objs:
            break

        ancestors = nx.ancestors(G, obj)
        descendants = nx.descendants(G, obj)
        overall_set = ancestors.union(descendants).union({obj})

        filtered_ocel = pm4py.filter_ocel_objects(ocel, overall_set)
        filtered_ocel.parameters["@@central_object"] = obj
        lst.append(filtered_ocel)

    return lst

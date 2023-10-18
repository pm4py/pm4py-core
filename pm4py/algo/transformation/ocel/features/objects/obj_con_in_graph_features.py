from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any
from enum import Enum
from pm4py.util import exec_utils
from pm4py.algo.transformation.ocel.graphs import object_interaction_graph, object_cobirth_graph, object_codeath_graph


class Parameters(Enum):
    GRAPH = "graph"


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    Extracts object-related features from the neighboring objects of a given object.

    Parameters
    ----------------
    ocel
        Object-centric event log
    parameters
        Parameters of the method, including:
        - Parameters.GRAPH => method that should be called on the object-centric event log to infer a graph

    Returns
    -----------------
    data
        Extracted feature values
    feature_names
        Feature names
    """
    if parameters is None:
        parameters = {}

    from pm4py.algo.transformation.ocel.features.objects import algorithm as object_based_features
    data_objects, feature_names_objects = object_based_features.apply(ocel)
    dct_dct_objects = object_based_features.transform_features_to_dict_dict(ocel, data_objects, feature_names_objects)

    graph_to_retrieve = exec_utils.get_param_value(Parameters.GRAPH, parameters, object_interaction_graph)
    graph0 = graph_to_retrieve.apply(ocel, parameters=parameters)
    graph = {}
    for el in graph0:
        if not el[0] in graph:
            graph[el[0]] = set()
        graph[el[0]].add(el[1])
        if graph_to_retrieve in [object_interaction_graph, object_cobirth_graph, object_codeath_graph]:
            # undirected
            if not el[1] in graph:
                graph[el[1]] = set()
            graph[el[1]].add(el[0])

    ordered_objects = list(ocel.objects[ocel.object_id_column])

    feature_names = []
    for x in feature_names_objects:
        feature_names.append("@@obj_graph_con_min_"+x)
        feature_names.append("@@obj_graph_con_max_"+x)

    data = []

    for obj in ordered_objects:
        arr = []

        con_obj = []
        if obj in graph:
            for y in graph[obj]:
                con_obj.append(dct_dct_objects[y])

        for x in feature_names_objects:
            if con_obj:
                min_v = min(y[x] for y in con_obj)
                max_v = max(y[x] for y in con_obj)
            else:
                min_v = 0
                max_v = 0
            arr.append(min_v)
            arr.append(max_v)
        data.append(arr)

    return data, feature_names

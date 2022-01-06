from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any
from pm4py.algo.transformation.ocel.graphs import object_interaction_graph


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    Adds for each object, and each object type, the number of interacting objects as a feature.

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

    ordered_objects = list(ocel.objects[ocel.object_id_column])

    object_types = list(ocel.objects[ocel.object_type_column].unique())

    object_type_association = ocel.objects[[ocel.object_id_column, ocel.object_type_column]].to_dict("records")
    object_type_association = {x[ocel.object_id_column]: x[ocel.object_type_column] for x in object_type_association}

    g0 = object_interaction_graph.apply(ocel, parameters=parameters)
    conn = {}

    for obj in ordered_objects:
        conn[obj] = set()

    for el in g0:
        conn[el[0]].add(el[1])
        conn[el[1]].add(el[0])

    data = []
    feature_names = ["@@object_interaction_graph_"+ot for ot in object_types]

    for obj in ordered_objects:
        data.append([])
        for ot in object_types:
            cot = [x for x in conn[obj] if object_type_association[x] == ot]
            data[-1].append(len(cot))

    return data, feature_names

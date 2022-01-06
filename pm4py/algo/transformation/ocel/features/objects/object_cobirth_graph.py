from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any
from pm4py.algo.transformation.ocel.graphs import object_cobirth_graph


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    Adds for each object the total number of cobirth object as feature

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

    g0 = object_cobirth_graph.apply(ocel, parameters=parameters)
    conn = {}

    for obj in ordered_objects:
        conn[obj] = set()

    for el in g0:
        conn[el[0]].add(el[1])
        conn[el[1]].add(el[0])

    data = []
    feature_names = ["@@object_cobirth"]

    for obj in ordered_objects:
        data.append([len(conn[obj])])

    return data, feature_names

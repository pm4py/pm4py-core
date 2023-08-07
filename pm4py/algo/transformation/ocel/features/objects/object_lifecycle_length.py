from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    Adds for each object the number of events in its lifecycle as feature

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
    lifecycle_length = ocel.relations.groupby(ocel.object_id_column).size().to_dict()

    data = []
    feature_names = ["@@object_lifecycle_length"]

    for obj in ordered_objects:
        if obj in lifecycle_length:
            data.append([lifecycle_length[obj]])
        else:
            data.append([0])

    return data, feature_names

from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    Adds for each object the number of unique activities in its lifecycle as feature

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
    lifecycle_unq = ocel.relations.groupby([ocel.object_id_column, ocel.event_activity]).first().reset_index()
    lifecycle_unq = lifecycle_unq.groupby(ocel.object_id_column).size().to_dict()

    data = []
    feature_names = ["@@object_lifecycle_unq_act"]

    for obj in ordered_objects:
        if obj in lifecycle_unq:
            data.append([lifecycle_unq[obj]])
        else:
            data.append([0])

    return data, feature_names

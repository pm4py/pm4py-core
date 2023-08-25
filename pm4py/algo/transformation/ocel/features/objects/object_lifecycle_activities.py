from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    Adds for each object an one-hot-encoding of the activities performed in its lifecycle

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
    activities = list(set(ocel.events[ocel.event_activity].unique()))
    lifecycle = ocel.relations.groupby(ocel.object_id_column)[ocel.event_activity].agg(list).to_dict()

    data = []
    feature_names = ["@@ocel_lif_activity_"+str(x) for x in activities]

    for obj in ordered_objects:
        data.append([])
        if obj in lifecycle:
            lif = lifecycle[obj]
        else:
            lif = []
        for act in activities:
            data[-1].append(len(list(x for x in lif if x == act)))

    return data, feature_names


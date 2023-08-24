from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    Adds for each object as features:
    - the duration of its lifecycle
    - the start timestamp
    - the end timestamp

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
    first_object_timestamp = ocel.relations.groupby(ocel.object_id_column).first()[ocel.event_timestamp].to_dict()
    last_object_timestamp = ocel.relations.groupby(ocel.object_id_column).last()[ocel.event_timestamp].to_dict()

    data = []
    feature_names = ["@@object_lifecycle_duration", "@@object_lifecycle_start_timestamp", "@@object_lifecycle_end_timestamp"]

    for obj in ordered_objects:
        if obj in first_object_timestamp:
            se = first_object_timestamp[obj].timestamp()
            ee = last_object_timestamp[obj].timestamp()
            data.append([ee - se, se, ee])
        else:
            data.append([0, 0, 0])

    return data, feature_names

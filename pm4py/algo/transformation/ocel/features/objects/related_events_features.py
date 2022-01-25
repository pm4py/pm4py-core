from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    Extracts for each object the minimum and the maximum value of the features for the events related to the object.

    Parameters
    -----------------
    ocel
        Object-centric event log
    parameters
        Parameters

    Returns
    -----------------
    data
        Extracted feature values
    feature_names
        Feature names
    """
    if parameters is None:
        parameters = {}

    from pm4py.algo.transformation.ocel.features.events import algorithm as event_based_features

    data_events, feature_names_events = event_based_features.apply(ocel, parameters=parameters)
    dct_dct_events = event_based_features.transform_features_to_dict_dict(ocel, data_events, feature_names_events, parameters=parameters)

    ordered_objects = list(ocel.objects[ocel.object_id_column])

    stream = ocel.relations[[ocel.event_id_column, ocel.object_id_column]].to_dict("records")
    obj_rel_evs = {}

    for cou in stream:
        if cou[ocel.object_id_column] not in obj_rel_evs:
            obj_rel_evs[cou[ocel.object_id_column]] = []
        obj_rel_evs[cou[ocel.object_id_column]].append(dct_dct_events[cou[ocel.event_id_column]])

    data = []
    feature_names = []
    for x in feature_names_events:
        feature_names.append("@@rel_eve_min_"+x)
        feature_names.append("@@rel_eve_max_"+x)

    for obj in ordered_objects:
        arr = []
        for x in feature_names_events:
            if obj in obj_rel_evs:
                min_v = min(y[x] for y in obj_rel_evs[obj])
                max_v = max(y[x] for y in obj_rel_evs[obj])
            else:
                min_v = 0
                max_v = 0
            arr.append(min_v)
            arr.append(max_v)
        data.append(arr)

    return data, feature_names

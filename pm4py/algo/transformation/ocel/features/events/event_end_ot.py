from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any
from pm4py.algo.filtering.ocel import ot_endpoints


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    Assigns to each event a feature that is 1 when the event completes the lifecycle of at least one object
    of a given type.

    Parameters
    ----------------
    ocel
        OCEL
    parameters
        Parameters of the algorithm

    Returns
    ----------------
    data
        Extracted feature values
    feature_names
        Feature names
    """
    if parameters is None:
        parameters = {}

    ordered_events = list(ocel.events[ocel.event_id_column])

    object_types = list(ocel.objects[ocel.object_type_column].unique())

    map_endpoints = {}
    for ot in object_types:
        map_endpoints[ot] = set(ot_endpoints.filter_end_events_per_object_type(ocel, ot, parameters=parameters).events[ocel.event_id_column])

    feature_names = ["@@event_end_"+ot for ot in object_types]
    data = []

    for ev in ordered_events:
        data.append([])
        for ot in object_types:
            data[-1].append(1 if ev in map_endpoints[ot] else 0)

    return data, feature_names

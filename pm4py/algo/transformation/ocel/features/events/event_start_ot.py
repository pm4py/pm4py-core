from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any
from pm4py.algo.filtering.ocel import ot_endpoints
from pm4py.util import pandas_utils


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    Assigns to each event a feature that is 1 when the event starts at least one object of a given type.

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

    ordered_events = parameters["ordered_events"] if "ordered_events" in parameters else ocel.events[
        ocel.event_id_column].to_numpy()

    object_types = ocel.objects.groupby(ocel.object_type_column)[ocel.object_id_column].agg(list).to_dict()
    endpoints = ocel.relations.groupby(ocel.object_id_column)[ocel.event_id_column].first().to_dict()

    map_endpoints = {ot: set() for ot in object_types}
    for ot in object_types:
        for obj in object_types[ot]:
            for ev in endpoints[obj]:
                map_endpoints[ot].add(ev)

    feature_names = ["@@event_start_"+ot for ot in object_types]
    data = []

    for ev in ordered_events:
        data.append([])
        for ot in object_types:
            data[-1].append(1.0 if ev in map_endpoints[ot] else 0.0)

    return data, feature_names

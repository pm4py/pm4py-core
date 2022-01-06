from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    Feature: assigns to each event the number of related objects.

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

    rel_objs = ocel.relations.groupby(ocel.event_id_column)[ocel.object_id_column].agg(list).to_dict()

    data = []
    feature_names = ["@@event_num_rel_objs"]

    for ev in ordered_events:
        data.append([len(rel_objs[ev])])

    return data, feature_names

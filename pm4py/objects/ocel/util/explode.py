from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any
from copy import deepcopy


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    """
    Explode an OCEL: an event associated to N objects is "split" to N events, each one associated to one object.

    Parameters
    -----------------
    ocel
        Object-centric event log
    parameters
        Possible parameters of the algorithm

    Returns
    -----------------
    ocel
        Exploded object-centric event log
    """
    if parameters is None:
        parameters = {}

    ocel = deepcopy(ocel)
    ocel.relations[ocel.event_id_column] = ocel.relations[ocel.event_id_column] + "_" + ocel.relations[ocel.object_id_column]
    ocel.events = ocel.relations.copy()
    del ocel.events[ocel.object_id_column]
    del ocel.events[ocel.object_type_column]

    return ocel

from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    """
    Forces the consistency of the OCEL, ensuring that the event/object identifier,
    event/object type are of type string and non-empty.

    Parameters
    --------------
    ocel
        OCEL
    parameters
        Possible parameters of the method

    Returns
    --------------
    ocel
        Consistent OCEL
    """
    if parameters is None:
        parameters = {}

    fields = {
        "events": ["ocel:eid", "ocel:activity"],
        "objects": ["ocel:oid", "ocel:type"],
        "relations": ["ocel:eid", "ocel:oid", "ocel:activity", "ocel:type"],
        "o2o": ["ocel:oid", "ocel:oid_2"],
        "e2e": ["ocel:eid", "ocel:eid_2"],
        "object_changes": ["ocel:oid"]
    }

    for tab in fields:
        df = getattr(ocel, tab)
        for fie in fields[tab]:
            df.dropna(subset=[fie], how="any", inplace=True)
            df[fie] = df[fie].astype("string")
            df.dropna(subset=[fie], how="any", inplace=True)
            df = df[df[fie].str.len() > 0]

    return ocel

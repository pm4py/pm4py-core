from typing import Dict, Any, Optional, List

from pm4py.objects.ocel.obj import OCEL


def related_events_dct(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None) -> Dict[str, Dict[str, List[str]]]:
    if parameters is None:
        parameters = {}

    object_types = ocel.relations[ocel.object_type_column].unique()
    dct = {}
    for ot in object_types:
        dct[ot] = ocel.relations[ocel.relations[ocel.object_type_column] == ot].groupby(ocel.object_id_column)[ocel.event_id_column].apply(
            list).to_dict()
    return dct

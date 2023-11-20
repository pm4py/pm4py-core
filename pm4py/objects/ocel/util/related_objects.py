from typing import Dict, Any, Optional, List

from pm4py.objects.ocel.obj import OCEL
from pm4py.util import pandas_utils


def related_objects_dct_per_type(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None) -> Dict[str, Dict[str, List[str]]]:
    if parameters is None:
        parameters = {}

    object_types = pandas_utils.format_unique(ocel.relations[ocel.object_type_column].unique())
    dct = {}
    for ot in object_types:
        dct[ot] = ocel.relations[ocel.relations[ocel.object_type_column] == ot].groupby(ocel.event_id_column)[ocel.object_id_column].apply(
            list).to_dict()
    return dct


def related_objects_dct_overall(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None) -> Dict[str, List[str]]:
    if parameters is None:
        parameters = {}

    evids = pandas_utils.format_unique(ocel.events[ocel.event_id_column].unique())
    dct = ocel.relations.groupby(ocel.event_id_column)[ocel.object_id_column].agg(list).to_dict()

    for evid in evids:
        if evid not in dct:
            dct[evid] = []

    return dct

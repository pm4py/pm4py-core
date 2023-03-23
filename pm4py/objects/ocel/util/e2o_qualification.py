from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any
from enum import Enum
from pm4py.util import exec_utils
from copy import copy

class Parameters(Enum):
    CONCATENER = "concatener"
    CONCAT_COLUMN = "concat_column"


def apply(ocel: OCEL, qualifier_type: str, parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    if parameters is None:
        parameters = {}

    concatener = exec_utils.get_param_value(Parameters.CONCATENER, parameters, "@@")
    concat_column = exec_utils.get_param_value(Parameters.CONCAT_COLUMN, parameters, "@@concat")

    ocel = copy(ocel)
    ocel.relations[concat_column] = ocel.relations[ocel.event_id_column] + concatener + ocel.relations[ocel.object_id_column]
    relations = ocel.relations.groupby(ocel.object_id_column)[ocel.event_id_column]

    if qualifier_type == "creation":
        relations = relations.first().to_dict()
        relations = {y + concatener + x: qualifier_type for x, y in relations.items()}
    elif qualifier_type == "termination":
        relations = relations.last().to_dict()
        relations = {y + concatener + x: qualifier_type for x, y in relations.items()}
    elif qualifier_type == "other":
        relations0 = relations.agg(list).to_dict()
        relations0 = {x: y[1:-1] for x, y in relations0.items()}
        relations0 = {x: y for x, y in relations0.items() if y}
        relations = {}
        for x, y in relations0.items():
            for y1 in y:
                relations[y1 + concatener + x] = qualifier_type

    ocel.relations[ocel.qualifier+"_2"] = ocel.relations[concat_column].map(relations)
    ocel.relations[ocel.qualifier+"_2"] = ocel.relations[ocel.qualifier+"_2"].fillna(ocel.relations[ocel.qualifier])
    ocel.relations[ocel.qualifier] = ocel.relations[ocel.qualifier+"_2"]

    del ocel.relations[ocel.qualifier+"_2"]
    del ocel.relations[concat_column]

    return ocel

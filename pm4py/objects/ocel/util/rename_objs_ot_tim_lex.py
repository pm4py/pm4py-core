from pm4py.objects.ocel.obj import OCEL
from copy import copy


def apply(ocel: OCEL) -> OCEL:
    """
    Rename objects given their object type, lifecycle start/end timestamps, and lexicographic order,

    Parameters
    -----------------
    ocel
        Object-centric event log

    Returns
    ----------------
    renamed_ocel
        Object-centric event log with renaming
    """
    objects_start = ocel.relations.groupby(ocel.object_id_column)[ocel.event_timestamp].first().to_dict()
    objects_end = ocel.relations.groupby(ocel.object_id_column)[ocel.event_timestamp].last().to_dict()
    objects_ot = ocel.objects[[ocel.object_id_column, ocel.object_type_column]].to_dict("records")
    objects_ot = {x[ocel.object_id_column]: x[ocel.object_type_column] for x in objects_ot}
    objects = list(ocel.objects[ocel.object_id_column].unique())
    objects.sort(key=lambda x: (objects_ot[x], objects_start[x], objects_end[x], x))
    objects = {objects[i]: objects_ot[objects[i]]+"_"+str(i) for i in range(len(objects))}

    ocel = copy(ocel)
    ocel.objects[ocel.object_id_column] = ocel.objects[ocel.object_id_column].map(objects)
    ocel.relations[ocel.object_id_column] = ocel.relations[ocel.object_id_column].map(objects)
    ocel.o2o[ocel.object_id_column] = ocel.o2o[ocel.object_id_column].map(objects)
    ocel.o2o[ocel.object_id_column + "_2"] = ocel.o2o[ocel.object_id_column + "_2"].map(objects)
    ocel.object_changes[ocel.object_id_column] = ocel.object_changes[ocel.object_id_column].map(objects)

    return ocel

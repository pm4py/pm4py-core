from pm4py.objects.ocel.obj import OCEL
from copy import deepcopy


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
    objects_ot0 = ocel.objects[[ocel.object_id_column, ocel.object_type_column]].to_dict("records")
    objects_ot0 = [(x[ocel.object_id_column], x[ocel.object_type_column]) for x in objects_ot0]
    objects_ot1 = {}

    for el in objects_ot0:
        if not el[1] in objects_ot1:
            objects_ot1[el[1]] = []
        objects_ot1[el[1]].append(el[0])

    overall_objects = {}
    keys = sorted(list(objects_ot1))
    for ot in keys:
        objects = objects_ot1[ot]
        objects.sort(key=lambda x: (objects_start[x], objects_end[x], x))
        objects = {objects[i]: ot + "_" + str(i+1) for i in range(len(objects))}
        overall_objects.update(objects)

    ocel = deepcopy(ocel)
    ocel.objects[ocel.object_id_column] = ocel.objects[ocel.object_id_column].map(overall_objects)
    ocel.relations[ocel.object_id_column] = ocel.relations[ocel.object_id_column].map(overall_objects)
    ocel.o2o[ocel.object_id_column] = ocel.o2o[ocel.object_id_column].map(overall_objects)
    ocel.o2o[ocel.object_id_column + "_2"] = ocel.o2o[ocel.object_id_column + "_2"].map(overall_objects)
    ocel.object_changes[ocel.object_id_column] = ocel.object_changes[ocel.object_id_column].map(overall_objects)

    return ocel

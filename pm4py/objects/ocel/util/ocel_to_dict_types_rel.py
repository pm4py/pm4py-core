from pm4py.objects.ocel.obj import OCEL
from typing import Dict, Union, Tuple
import pandas as pd


def apply(ocel: OCEL) -> Dict[str, Dict[Union[str, Tuple[str, str]], pd.DataFrame]]:
    """
    Gets from an object-centric event log (OCEL)
    a dictionary associating to every event/object/e2o/o2o/change type
    a dataframe containing the associated information.
    This effectively splits the information of different event/object types
    in dense dataframes.

    Parameters
    -------------
    ocel
        Object-centric event log

    Returns
    -----------
    dct_types_rel
        Dictionary associating to every type the corresponding dense table.

        Keys at the first level:
        - ev_types: pointing to the different event types of the object-centric event log
        - obj_types: pointing to the different object types of the object-centric event log
        - e2o: pointing to the different event-object relationships of the object-centric event log
        - o2o: pointing to the different object-object relationships of the object-centric event log
        - object_changes: pointing to temporal changes in the attributes of the different object types of an OCEL

        Keys at the second level:
        - for "ev_types", "obj_types" and "object_changes": the name of the event/object type related to the dense table
        - for "e2o": a tuple in which the first element is an event type, and the second element is an object type
        - for "o2o": a tuple in which the two elements are interconnected object types

        Value: a Pandas dataframe (dense table).
    """
    ev_types_list = list(ocel.events[ocel.event_activity].unique())
    obj_types_list = list(ocel.objects[ocel.object_type_column].unique())
    e2o_list = list(ocel.relations.groupby([ocel.event_activity, ocel.object_type_column]).size().to_dict())

    obj_type_map = ocel.objects[[ocel.object_id_column, ocel.object_type_column]].to_dict("records")
    obj_type_map = {x[ocel.object_id_column]: x[ocel.object_type_column] for x in obj_type_map}
    overall_o2o = ocel.o2o.copy()
    overall_o2o[ocel.object_type_column] = overall_o2o[ocel.object_id_column].map(obj_type_map)
    overall_o2o[ocel.object_type_column+"_2"] = overall_o2o[ocel.object_id_column+"_2"].map(obj_type_map)

    o2o_list = list(overall_o2o.groupby([ocel.object_type_column, ocel.object_type_column+"_2"]).size().to_dict())
    changes_list = list(ocel.object_changes[ocel.object_type_column].unique())

    dct_types_rel = {"ev_types": {}, "obj_types": {}, "e2o": {}, "o2o": {}, "changes": {}}

    for evt in ev_types_list:
        events = ocel.events[ocel.events[ocel.event_activity] == evt]
        events.dropna(axis="columns", how="all")
        dct_types_rel["ev_types"][evt] = events

    for objt in obj_types_list:
        objects = ocel.objects[ocel.objects[ocel.object_type_column] == objt]
        objects.dropna(axis="columns", how="all")
        dct_types_rel["obj_types"][objt] = objects

    for e2ot in e2o_list:
        e2o = ocel.relations[(ocel.relations[ocel.event_activity] == e2ot[0]) & (ocel.relations[ocel.object_type_column] == e2ot[1])]
        e2o.dropna(axis="columns", how="all")
        dct_types_rel["e2o"][e2ot] = e2o

    for o2ot in o2o_list:
        o2o = overall_o2o[(overall_o2o[ocel.object_type_column] == o2ot[0]) & (overall_o2o[ocel.object_type_column+"_2"] == o2ot[1])]
        o2o.dropna(axis="columns", how="all")
        dct_types_rel["o2o"][o2ot] = o2o

    for objt in changes_list:
        objects = ocel.object_changes[ocel.object_changes[ocel.object_type_column] == objt]
        objects.dropna(axis="columns", how="all")
        dct_types_rel["changes"][objt] = objects

    return dct_types_rel

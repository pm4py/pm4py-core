import pandas as pd
from pycelonis.ems.data_integration.data_pool import DataPool, DataModel
from pycelonis.celonis import DataIntegration, Celonis
from typing import Optional, Dict, Any, Union
from pm4py.objects.ocel.obj import OCEL
import uuid
from pm4py.objects.ocel.util import names_stripping


def apply(ocel: OCEL, c: Union[Celonis, DataIntegration], data_pool_name: str,
          parameters: Optional[Dict[Any, Any]] = None) -> DataModel:
    """
    Uploads an OCEL to a Celonis data model

    Parameters
    --------------
    ocel
        Traditional log object (EventLog, EventStream, Pandas dataframe)
    c
        Data integration object (of Pycelonis)
    data_pool_name
        Name of the data pool (into which the OCEL should be uploaded)

    Returns
    -------------
    data_model
        Data model object
    """
    if parameters is None:
        parameters = {}

    if isinstance(c, Celonis):
        c = c.data_integration

    event_types = ocel.events[ocel.event_activity].unique()
    object_types = ocel.objects[ocel.object_type_column].unique()

    event_types_map = {}
    object_types_map = {}

    for et in event_types:
        event_types_map[et] = names_stripping.apply(et)
    for ot in object_types:
        object_types_map[ot] = names_stripping.apply(ot)

    events = ocel.events.copy()
    objects = ocel.objects.copy()
    relations = ocel.relations.copy()[
        [ocel.event_id_column, ocel.event_activity, ocel.object_id_column, ocel.object_type_column]]

    events[ocel.event_activity] = events[ocel.event_activity].map(event_types_map)
    objects[ocel.object_type_column] = objects[ocel.object_type_column].map(object_types_map)
    relations[ocel.event_activity] = relations[ocel.event_activity].map(event_types_map)
    relations[ocel.object_type_column] = relations[ocel.object_type_column].map(object_types_map)

    events.rename(columns={ocel.event_id_column: "ID", ocel.event_activity: "Type", ocel.event_timestamp: "Time"},
                  inplace=True)
    objects.rename(columns={ocel.object_id_column: "ID", ocel.object_type_column: "Type"}, inplace=True)
    relations.rename(
        columns={ocel.event_id_column: "EventID", ocel.event_activity: "EventType", ocel.object_id_column: "ObjectID",
                 ocel.object_type_column: "ObjectType"}, inplace=True)

    event_type_tables = {}
    object_type_tables = {}

    for et, df in events.groupby("Type"):
        event_type_tables["e_celonis_" + et] = df.dropna(axis="columns", how="all")

    for ot, df in objects.groupby("Type"):
        object_type_tables["o_celonis_" + ot] = df.dropna(axis="columns", how="all")

    # add an hypotetical SalesOrderItem object type, with empty columns
    df = pd.DataFrame({"ID": [str(uuid.uuid4())], "Type": ["SalesOrderItem"]})
    object_type_tables["o_celonis_SalesOrderItem"] = df

    try:
        data_pool: DataPool = c.get_data_pools().find(data_pool_name)
    except:
        data_pool: DataPool = c.create_data_pool(data_pool_name)

    for index, name in enumerate(object_type_tables):
        print("object type table", index + 1, "of", len(object_type_tables), ":", name)
        df = object_type_tables[name]
        try:
            data_pool.create_table(df, name)
        except:
            data_pool.create_table(df, name, force=True, drop_if_exists=True)

    for index, name in enumerate(event_type_tables):
        print("event type table", index + 1, "of", len(event_type_tables), ":", name)
        df = event_type_tables[name]
        try:
            data_pool.create_table(df, name)
        except:
            data_pool.create_table(df, name, force=True, drop_if_exists=True)

    data_pool.create_table(relations, "r_celonis_SalesOrderItem", force=True, drop_if_exists=True)

    data_model: DataModel = data_pool.create_data_model(str(uuid.uuid4()))
    tables_dict = {}

    for index, name in enumerate(event_type_tables):
        tab = data_model.add_table(name, name)
        tables_dict[name] = tab.id

    for index, name in enumerate(object_type_tables):
        tab = data_model.add_table(name, name)
        tables_dict[name] = tab.id

    tab = data_model.add_table("r_celonis_SalesOrderItem", "r_celonis_SalesOrderItem")
    tables_dict["r_celonis_SalesOrderItem"] = tab.id

    for index, name in enumerate(event_type_tables):
        data_model.create_foreign_key(tables_dict[name], tables_dict["r_celonis_SalesOrderItem"], [("ID", "EventID")])

    for index, name in enumerate(object_type_tables):
        data_model.create_foreign_key(tables_dict[name], tables_dict["r_celonis_SalesOrderItem"], [("ID", "ObjectID")])

    data_model.reload()

    return data_model

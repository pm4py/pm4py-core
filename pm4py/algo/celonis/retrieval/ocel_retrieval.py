from pycelonis.ems.data_integration.data_pool import DataPool, DataModel
from typing import Dict, Optional, Any
from pm4py.objects.ocel.obj import OCEL
from pm4py.algo.celonis.retrieval import dm_retrieval
import uuid
import pandas as pd
from pm4py.util import exec_utils
from enum import Enum


class Parameters(Enum):
    NEW_REL_TABLE = "new_rel_table"


def apply(data_pool: DataPool, data_model: DataModel, parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    """
    Retrieves an OCEL from a Celonis data model

    Parameters
    --------------
    data_pool
        Data pool
    data_model
        Data model
    parameters
        Possible parameters of the algorithm, including:
        - Parameters.NEW_REL_TABLE => additional copy of the relationship table that is created in order to overcome the limitations of SAOLA in retrieving the table

    Returns
    --------------
    ocel
        Object-centric event log
    """
    if parameters is None:
        parameters = {}

    new_rel_table = exec_utils.get_param_value(Parameters.NEW_REL_TABLE, parameters, "relationships_downloads_pm4py")

    tables = data_model.get_tables()
    relationship_table = [x.name for x in tables if x.name.startswith("r_")][0]

    data_job = data_pool.create_job(str(uuid.uuid4()))
    task = data_job.create_transformation(str(uuid.uuid4()))

    task.update_statement("""
DROP TABLE IF EXISTS """ + new_rel_table + """;
CREATE TABLE """ + new_rel_table + """ AS (SELECT * FROM """ + relationship_table + ");")
    data_job.execute()

    try:
        data_model.add_table(new_rel_table, new_rel_table)
        data_model.reload()
    except:
        pass

    dct = dm_retrieval.apply(data_model, parameters=parameters)
    events = [dct[x] for x in dct if x.startswith("e_")]
    objects = [dct[x] for x in dct if x.startswith("o_")]
    relations = dct["relationships_downloads_pm4py"]

    events = pd.concat(events)
    objects = pd.concat(objects)

    events.rename(columns={"ID": "ocel:eid", "Type": "ocel:activity", "Time": "ocel:timestamp"}, inplace=True)
    objects.rename(columns={"ID": "ocel:oid", "Type": "ocel:type"}, inplace=True)
    relations.rename(columns={"EventID": "ocel:eid", "EventType": "ocel:activity", "ObjectID": "ocel:oid",
                              "ObjectType": "ocel:type"}, inplace=True)

    ocel = OCEL(events=events, objects=objects, relations=relations)

    return ocel

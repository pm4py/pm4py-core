from pycelonis.ems.data_integration.data_pool import DataPool, DataModel
from pycelonis.celonis import DataIntegration, Celonis
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd
from typing import Optional, Dict, Any, Union
from enum import Enum
from pm4py.util import exec_utils, constants, xes_constants
import uuid


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY


def apply(log_obj: Union[EventLog, EventStream, pd.DataFrame], c: Union[Celonis, DataIntegration], data_pool_name: str, parameters: Optional[Dict[Any, Any]] = None) -> DataModel:
    """
    Uploads a traditional event log to a Celonis data model

    Parameters
    --------------
    log_obj
        Traditional log object (EventLog, EventStream, Pandas dataframe)
    c
        Data integration object (of Pycelonis)
    data_pool_name
        Name of the data pool (into which the log should be uploaded)
    parameters
        Possible parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY => the column that should be used as activity
        - Parameters.TIMESTAMP_KEY => the column that should be used as timestamp
        - Parameters.CASE_ID_KEY => the column that should be used as case identifier

    Returns
    -------------
    data_model
        Data model object
    """
    if parameters is None:
        parameters = {}

    if isinstance(c, Celonis):
        c = c.data_integration

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)
    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)

    log_obj = log_converter.apply(log_obj, variant=log_converter.Variants.TO_DATA_FRAME, parameters=parameters)

    try:
        data_pool: DataPool = c.get_data_pools().find(data_pool_name)
    except:
        data_pool: DataPool = c.create_data_pool(data_pool_name)

    data_pool.create_table(log_obj, "activity_table", drop_if_exists=True, force=True)

    data_model: DataModel = data_pool.create_data_model(str(uuid.uuid4()))
    table = data_model.add_table("activity_table", "activity_table")

    process_conf = data_model.create_process_configuration(table.id, case_id_key, activity_key, timestamp_key)

    data_model.reload()

    return data_model

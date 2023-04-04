from pycelonis.ems.data_integration.data_pool import DataPool, DataModel
from typing import Dict, Optional, Any
from pm4py.algo.celonis.retrieval import dm_retrieval
import pandas as pd
from pm4py.util import constants, xes_constants, exec_utils
from enum import Enum


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY


def apply(data_pool: DataPool, data_model: DataModel, parameters: Optional[Dict[Any, Any]] = None) -> pd.DataFrame:
    """
    Retrieves a traditional event log from a data model in Celonis

    Parameters
    --------------
    data_pool
        Data pool
    data_model
        Data model
    parameters
        Parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY => the column to be used as activity
        - Parameters.CASE_ID_KEY => the column to be used as case ID
        - Parameters.TIMESTAMP_KEY => the column to be used as timestamp

    Returns
    --------------
    dataframe
        Pandas dataframe
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)

    dct = dm_retrieval.apply(data_model, parameters=parameters)

    tables = data_model.get_tables()
    tables = {x.id: x.name for x in tables}

    process_conf = list(data_model.get_process_configurations())[0]

    dataframe = dct[tables[process_conf.activity_table_id]]
    columns = {}

    their_case_id = process_conf.case_id_column
    their_activity = process_conf.activity_column
    their_timestamp = process_conf.timestamp_column

    if their_case_id != case_id_key:
        columns[their_case_id] = case_id_key

    if their_activity != activity_key:
        columns[their_activity] = activity_key

    if their_timestamp != timestamp_key:
        columns[their_timestamp] = timestamp_key

    if columns:
        dataframe.rename(columns=columns, inplace=True)

    return dataframe

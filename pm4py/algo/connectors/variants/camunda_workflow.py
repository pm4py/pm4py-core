from typing import Optional, Dict, Any
from enum import Enum
from pm4py.util import exec_utils
import pandas as pd


class Parameters(Enum):
    CONNECTION_STRING = "connection_string"


def apply(conn, parameters: Optional[Dict[Any, Any]] = None) -> pd.DataFrame:
    """
    Extracts an event log from the Camunda workflow system

    Parameters
    ---------------
    conn
        (if provided) ODBC connection object to the database (offering cursors)
    parameters
        Parameters of the algorithm, including:
        - Parameters.CONNECTION_STRING => connection string that is used (if no connection is provided)

    Returns
    ---------------
    dataframe
        Pandas dataframe
    """
    if parameters is None:
        parameters = {}

    import pm4py

    connection_string = exec_utils.get_param_value(Parameters.CONNECTION_STRING, parameters, None)

    if conn is None:
        import pyodbc
        conn = pyodbc.connect(connection_string)

    curs = conn.cursor()

    query = """
    SELECT
    pi.PROC_DEF_KEY_ AS "processID",
    ai.EXECUTION_ID_ AS "case:concept:name",
    ai.ACT_NAME_ AS "concept:name",
    ai.START_TIME_ AS "time:timestamp",
    ai.ASSIGNEE_ AS "org:resource"
    FROM
        act_hi_procinst pi
    JOIN
        act_hi_actinst ai ON pi.PROC_INST_ID_ = ai.PROC_INST_ID_
    ORDER BY
        pi.PROC_INST_ID_,
        ai.EXECUTION_ID_,
        ai.START_TIME_;
    """
    columns = ["processID", "case:concept:name", "concept:name", "time:timestamp", "org:resource"]

    curs.execute(query)
    dataframe = curs.fetchall()
    dataframe = pd.DataFrame.from_records(dataframe, columns=columns)
    dataframe = pm4py.format_dataframe(dataframe)

    curs.close()
    conn.close()

    return dataframe

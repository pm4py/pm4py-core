'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''

from typing import Optional, Dict, Any
from enum import Enum
from pm4py.util import exec_utils, pandas_utils
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
    dataframe = pandas_utils.instantiate_dataframe_from_records(dataframe, columns=columns)
    dataframe = pm4py.format_dataframe(dataframe)

    curs.close()
    conn.close()

    return dataframe

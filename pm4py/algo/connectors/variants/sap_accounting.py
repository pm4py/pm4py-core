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
    PREFIX = "prefix"


def apply(conn, parameters: Optional[Dict[Any, Any]] = None) -> pd.DataFrame:
    """
    Extracts an event log for the SAP Accounting process

    Parameters
    ---------------
    conn
        (if provided) ODBC connection object to the database (offering cursors)
    parameters
        Parameters of the algorithm, including:
        - Parameters.CONNECTION_STRING => connection string that is used (if no connection is provided)
        - Parameters.PREFIX => prefix to add to the table names (example SAPSR3.)

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

    prefix = exec_utils.get_param_value(Parameters.PREFIX, parameters, "")

    curs = conn.cursor()

    query = """
    SELECT * FROM
    (SELECT MANDT || '-' || BUKRS || '-' || GJAHR || '-' || BELNR AS "case:concept:name", 'Create Financial Document - ' || BLART AS "concept:name", CPUDT || ' ' || CPUTM AS "time:timestamp", USNAM AS "org:resource", BLART FROM """+prefix+"""BKPF
    UNION
    SELECT MANDT || '-' || BUKRS || '-' || GJAHR || '-' || AUGBL AS "case:concept:name", 'Clear Customer Document' AS "concept:name", AUGDT || ' 235958' AS "time:timestamp", NULL AS "org:resource", NULL AS BLART FROM """+prefix+"""BSAD
    UNION
    SELECT MANDT || '-' || BUKRS || '-' || GJAHR || '-' || AUGBL AS "case:concept:name", 'Clear Vendor Document' AS "concept:name", AUGDT || ' 235959' AS "time:timestamp", NULL AS "org:resource", NULL AS BLART FROM """+prefix+"""BSAK)
    ORDER BY "case:concept:name", "time:timestamp";
    """
    columns = ["case:concept:name", "concept:name", "time:timestamp", "org:resource", "BLART"]

    curs.execute(query)
    dataframe = curs.fetchall()
    dataframe = pandas_utils.instantiate_dataframe_from_records(dataframe, columns=columns)
    dataframe = pm4py.format_dataframe(dataframe)

    curs.close()
    conn.close()

    return dataframe

from typing import Optional, Dict, Any
from enum import Enum
from pm4py.util import exec_utils
import pandas as pd


class Parameters(Enum):
    CONNECTION_STRING = "connection_string"
    PREFIX = "prefix"


def apply(conn, parameters: Optional[Dict[Any, Any]] = None) -> pd.DataFrame:
    """
    Extracts an event log for the SAP Order-to-Cash process

    Parameters
    ---------------
    conn
        (if provided) connection object to the database (offering cursors)
    parameters
        Parameters of the algorithm, including:
        - Parameters.CONNECTION_STRING => ODBC connection string that is used (if no connection is provided)
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
(SELECT
    T1.VBELN AS "case:concept:name",
    DECODE(T1.TYPE, 'C', 'Create Sales Document', 'D', 'Create Delivery') AS "concept:name",
    T1.TIMESTAMP AS "time:timestamp",
    T1.USERNAME AS "org:resource"
FROM
    (
        SELECT
            'C' AS TYPE,
            VBAK.VBELN,
            VBAK.ERDAT || ' ' || VBAK.ERZET AS TIMESTAMP,
            VBAK.ERNAM AS USERNAME
        FROM
            """+prefix+"""VBAK
        UNION ALL
        SELECT
            'D' AS TYPE,
            VBFA.VBELV AS VBELN,
            LIKP.ERDAT || ' ' || LIKP.ERZET AS TIMESTAMP,
            LIKP.ERNAM AS USERNAME
        FROM
            """+prefix+"""LIKP
        JOIN """+prefix+"""VBFA ON LIKP.VBELN = VBFA.VBELN
        WHERE
            VBFA.VBTYP_N = 'J'
    ) T1 )
    UNION
    (
    SELECT
    VBFA.VBELN AS "case:concept:name",
    TSTCT.TTEXT AS "concept:name",
    CDHDR.UDATE || ' ' || CDHDR.UTIME AS "time:timestamp",
    CDHDR.USERNAME AS "org:resource"
FROM
    """+prefix+"""VBFA VBFA
    JOIN """+prefix+"""VBAK VBAK ON VBFA.VBELN = VBAK.VBELN
    JOIN """+prefix+"""VBAP VBAP ON VBAK.VBELN = VBAP.VBELN
    JOIN """+prefix+"""CDHDR CDHDR ON VBFA.VBELN = CDHDR.OBJECTID
    JOIN """+prefix+"""TSTCT TSTCT ON CDHDR.TCODE = TSTCT.TCODE
WHERE
    VBFA.VBTYP_N = 'C'
    AND TSTCT.SPRSL = 'E'
    )
    """
    columns = ["case:concept:name", "concept:name", "time:timestamp", "org:resource"]

    curs.execute(query)
    dataframe = curs.fetchall()
    dataframe = pd.DataFrame.from_records(dataframe, columns=columns)
    dataframe = pm4py.format_dataframe(dataframe)

    curs.close()
    conn.close()

    return dataframe

from pm4py.objects.ocel.obj import OCEL
from typing import Dict, Any, Optional


def apply(ocel: OCEL, target_path: str, parameters: Optional[Dict[Any, Any]] = None):
    """
    Exports an OCEL to a SQLite database using Pandas

    Parameters
    ---------------
    ocel
        Object-centric event log
    target_path
        Path to the SQLite database
    parameters
        Parameters of the exporter
    """
    if parameters is None:
        parameters = {}

    import sqlite3

    conn = sqlite3.connect(target_path)

    ocel.events.to_sql("EVENTS", conn, index=False)
    ocel.relations.to_sql("RELATIONS", conn, index=False)
    ocel.objects.to_sql("OBJECTS", conn, index=False)

    conn.close()

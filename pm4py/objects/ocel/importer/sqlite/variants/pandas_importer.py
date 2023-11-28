from pm4py.objects.ocel.obj import OCEL
from typing import Dict, Any, Optional
import pandas as pd
from pm4py.objects.ocel.util import ocel_consistency
from pm4py.objects.ocel.util import filtering_utils
from pm4py.util.dt_parsing.variants import strpfromiso
from pm4py.util import pandas_utils, constants as pm4_constants


def apply(file_path: str, parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    """
    Imports an OCEL from a SQLite database using Pandas

    Parameters
    --------------
    file_path
        Path to the SQLite database
    parameters
        Parameters of the import

    Returns
    --------------
    ocel
        Object-centric event log
    """
    if parameters is None:
        parameters = {}

    import sqlite3

    conn = sqlite3.connect(file_path)

    events = pd.read_sql("SELECT * FROM EVENTS", conn)
    objects = pd.read_sql("SELECT * FROM OBJECTS", conn)
    relations = pd.read_sql("SELECT * FROM RELATIONS", conn)

    events["ocel:timestamp"] = pandas_utils.dataframe_column_string_to_datetime(events["ocel:timestamp"],
                                                              utc=pm4_constants.ENABLE_DATETIME_COLUMNS_AWARE,
                                                              format=pm4_constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)

    relations["ocel:timestamp"] = pandas_utils.dataframe_column_string_to_datetime(events["ocel:timestamp"],
                                                              utc=pm4_constants.ENABLE_DATETIME_COLUMNS_AWARE,
                                                              format=pm4_constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)

    events["ocel:timestamp"] = strpfromiso.fix_dataframe_column(events["ocel:timestamp"])
    relations["ocel:timestamp"] = strpfromiso.fix_dataframe_column(relations["ocel:timestamp"])

    ocel = OCEL(events=events, objects=objects, relations=relations, parameters=parameters)
    ocel = ocel_consistency.apply(ocel, parameters=parameters)
    ocel = filtering_utils.propagate_relations_filtering(ocel, parameters=parameters)

    return ocel

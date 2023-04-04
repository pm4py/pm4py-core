import pandas as pd
from typing import Dict, Optional, Any
from io import BytesIO
from pycelonis.pql.pql import PQL, PQLColumn
from pycelonis.service.integration.service import ExportType
from pycelonis.ems.data_integration.data_pool import DataModel


def apply(data_model: DataModel, parameters: Optional[Dict[Any, Any]] = None) -> Dict[str, pd.DataFrame]:
    """
    Retrieves the tables of a data model in Celonis

    Parameters
    --------------
    data_model
        Celonis data model

    Returns
    -------------
    dct
        Dictionary associating each name to a dataframe extracted from the data model
    """
    if parameters is None:
        parameters = {}

    dct = {}
    tables = data_model.get_tables()
    for table in tables:
        table2 = data_model.get_table(table.id)
        columns = table2.get_columns()
        buffer = BytesIO()
        excluded_columns = set()
        for i in range(2):
            try:
                pql = PQL()
                for col in columns:
                    if not col.name.startswith("_"):
                        fname = "\"" + table2.name + "\".\"" + col.name + "\""
                        if fname not in excluded_columns:
                            pql.add(PQLColumn(query=fname, name=col.name))
                dexp = data_model.create_data_export(query=pql, export_type=ExportType.PARQUET)
                dexp.wait_for_execution()
                chunks = dexp.get_chunks()
                for chunk in chunks:
                    buffer.write(chunk.read())
                df = pd.read_parquet(buffer)
                dct[table.name] = df
                break
            except Exception as e:
                e = str(e)
                cols = e.split(" is missing")
                for c in cols:
                    c = c.split("Column ")[-1]
                    excluded_columns.add(c)
    return dct

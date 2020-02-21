import pyarrow.parquet as pq
from pm4py.objects.log.util import dataframe_utils


COLUMNS = "columns"


def apply(path, parameters=None):
    """
    Import a Parquet file

    Parameters
    -------------
    path
        Path of the file to import
    parameters
        Parameters of the algorithm, possible values:
            columns -> columns to import from the Parquet file

    Returns
    -------------
    df
        Pandas dataframe
    """
    if parameters is None:
        parameters = {}

    columns = parameters[COLUMNS] if COLUMNS in parameters else None

    if columns:
        df = pq.read_pandas(path, columns=columns).to_pandas()
    else:
        df = pq.read_pandas(path).to_pandas()

    return dataframe_utils.legacy_parquet_support(df)


def import_table(path, parameters=None):
    """
    Imports a Pyarrow table from a Parquet file

    Parameters
    ------------
    path
        Path to the Parquet file
    parameters
        Parameters of the algorithm

    Returns
    ------------
    table
        Pyarrow table
    """
    if parameters is None:
        parameters = {}

    columns = parameters[COLUMNS] if COLUMNS in parameters else None
    if columns:
        table = pq.read_table(path, columns=columns)
    else:
        table = pq.read_table(path)

    return table


def import_log(path, parameters=None):
    """
    Imports an event log from a Parquet file

    Parameters
    --------------
    path
        Path to the Parquet file
    parameters
        Parameters of the algorithm

    Returns
    --------------
    log
        Event log
    """
    if parameters is None:
        parameters = {}

    table = import_table(path, parameters=parameters)

    return dataframe_utils.table_to_log(table, parameters=parameters)

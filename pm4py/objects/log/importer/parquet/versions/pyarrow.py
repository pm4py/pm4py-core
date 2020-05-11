import pyarrow.parquet as pq
from pm4py.objects.log.util import dataframe_utils
import deprecation
from pm4py.util import exec_utils
from pm4py.objects.log.importer.parquet.parameters import Parameters

COLUMNS = Parameters.COLUMNS.value


@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Please import the parquet to a pandas df, then convert it to an event log, if needed')
def apply(path, parameters=None):
    """
    Import a Parquet file

    Parameters
    -------------
    path
        Path of the file to import
    parameters
        Parameters of the algorithm, possible values:
            Parameters.COLUMNS -> columns to import from the Parquet file

    Returns
    -------------
    df
        Pandas dataframe
    """
    if parameters is None:
        parameters = {}

    columns = exec_utils.get_param_value(Parameters.COLUMNS, parameters, None)

    if columns:
        df = pq.read_pandas(path, columns=columns).to_pandas()
    else:
        df = pq.read_pandas(path).to_pandas()

    return dataframe_utils.legacy_parquet_support(df)


@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Please import the parquet to a pandas df, then convert it to an event log, if needed')
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

    columns = exec_utils.get_param_value(Parameters.COLUMNS, parameters, None)

    if columns:
        table = pq.read_table(path, columns=columns)
    else:
        table = pq.read_table(path)

    return table


@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Please import the parquet to a pandas df, then convert it to an event log, if needed')
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

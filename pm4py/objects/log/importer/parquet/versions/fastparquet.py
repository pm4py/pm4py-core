from fastparquet import ParquetFile
from pm4py.objects.log.util import dataframe_utils
import deprecation
from pm4py.objects.log.importer.parquet.parameters import Parameters
from pm4py.util import exec_utils

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

    pf = ParquetFile(path)

    if columns:
        df = pf.to_pandas(columns)
    else:
        df = pf.to_pandas()

    return dataframe_utils.legacy_parquet_support(df)

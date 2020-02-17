from fastparquet import ParquetFile
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
    pf = ParquetFile(path)

    if columns:
        df = pf.to_pandas(columns)
    else:
        df = pf.to_pandas()

    return dataframe_utils.legacy_parquet_support(df)

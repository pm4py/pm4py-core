import pyarrow.parquet as pq

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
        columns = [x.replace(":", "AAA") for x in columns]
        df = pq.read_pandas(path, columns=columns).to_pandas()
    else:
        df = pq.read_pandas(path, columns=columns).to_pandas()
    df.columns = [x.replace("AAA", ":") for x in df.columns]

    return df

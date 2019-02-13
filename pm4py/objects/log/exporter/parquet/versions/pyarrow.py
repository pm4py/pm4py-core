import pyarrow as pa
import pyarrow.parquet as pq


def apply(df, path, parameters=None):
    """
    Exports a dataframe to a Parquet file

    Parameters
    ------------
    df
        Dataframe
    path
        Path
    parameters
        Possible parameters of the algorithm
    """
    if parameters is None:
        parameters = {}

    df.columns = [x.replace(":", "AAA") for x in df.columns]
    df = pa.Table.from_pandas(df)
    pq.write_table(df, path)

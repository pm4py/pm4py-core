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

    df.to_parquet(path)

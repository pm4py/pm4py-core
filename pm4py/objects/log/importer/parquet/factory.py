from pm4py.objects.log.importer.parquet.versions import pyarrow

PYARROW = "pyarrow"

VERSIONS = {PYARROW: pyarrow.apply}

COLUMNS = "columns"


def apply(path, parameters=None, variant=PYARROW):
    """
    Import a Parquet file

    Parameters
    -------------
    path
        Path of the file to import
    parameters
        Parameters of the algorithm, possible values:
            columns -> columns to import from the Parquet file
    variant
        Variant of the algorithm, possible values: pyarrow

    Returns
    -------------
    df
        Pandas dataframe
    """
    return VERSIONS[variant](path, parameters=parameters)


def import_log(path, parameters=None, variant=PYARROW):
    """
    Import a Parquet file

    Parameters
    -------------
    path
        Path of the file to import
    parameters
        Parameters of the algorithm, possible values:
            columns -> columns to import from the Parquet file
    variant
        Variant of the algorithm, possible values: pyarrow

    Returns
    -------------
    df
        Pandas dataframe
    """
    return VERSIONS[variant](path, parameters=parameters)


def import_df(path, parameters=None, variant=PYARROW):
    """
    Import a Parquet file

    Parameters
    -------------
    path
        Path of the file to import
    parameters
        Parameters of the algorithm, possible values:
            columns -> columns to import from the Parquet file
    variant
        Variant of the algorithm, possible values: pyarrow

    Returns
    -------------
    df
        Pandas dataframe
    """
    return VERSIONS[variant](path, parameters=parameters)

import os
import tempfile

import pandas as pd

from pm4py.util.versions import check_pandas_ge_024


def import_dataframe_from_path_wo_timeconversion(path, sep=',', quotechar=None, nrows=None):
    """
    Imports a dataframe from the given path (without doing the timestamp columns conversion)

    Parameters
    ----------
    path:
        Input CSV file path
    sep:
        column separator
    quotechar
        (if specified) Character that starts/end big strings in CSV
    nrows
        (if specified) Maximum number of rows to read from the CSV

     Returns
    -------
    pd
        Pandas dataframe
    """
    if quotechar:
        if nrows:
            df = pd.read_csv(path, sep=sep, quotechar=quotechar, nrows=nrows)
        else:
            df = pd.read_csv(path, sep=sep, quotechar=quotechar)
    else:
        if nrows:
            df = pd.read_csv(path, sep=sep, nrows=nrows)
        else:
            df = pd.read_csv(path, sep=sep)

    return df


def import_dataframe_from_csv_string(csv_string, sep=',', quotechar=None, nrows=None, sort=False,
                                     sort_field="time:timestamp", timest_format=None, timest_columns=None):
    """
    Import dataframe from CSV string

    Parameters
    -----------
    csv_string
        CSV string
    sep
        CSV columns delimiter
    quotechar
        (if specified) Character that starts/end big strings in CSV
    nrows
        (if specified) Maximum number of rows to read from the CSV
    sort
        Boolean value that tells if the CSV should be ordered
    sort_field
        If sort option is enabled, then the CSV is automatically sorted by the specified column
    timest_format
        (If provided) Format of the timestamp columns in the CSV file
    timest_columns
        Columns of the CSV that shall be converted into timestamp

    Returns
    -----------
    df
        Pandas dataframe
    """
    fp = tempfile.NamedTemporaryFile(suffix='.csv')
    fp.close()
    with open(fp.name, 'w') as f:
        f.write(csv_string)
    df = import_dataframe_from_path(fp.name, sep=sep, quotechar=quotechar, nrows=nrows, sort=sort,
                                    sort_field=sort_field, timest_format=timest_format, timest_columns=timest_columns)
    os.remove(fp.name)
    return df


def convert_caseid_column_to_str(df, case_id_glue="case:concept:name"):
    """
    Convert Case ID column to string

    Parameters
    -----------
    df
        Pandas dataframe
    case_id_glue
        Case ID glue (that is used to connect the traces)

    Returns
    -----------
    df
        Pandas dataframe with case ID column as string
    """
    df[case_id_glue] = df[case_id_glue].astype(str)
    return df


def convert_timestamp_columns_in_df(df, timest_format=None, timest_columns=None):
    """
    Convert all dataframe columns in a dataframe

    Parameters
    -----------
    df
        Dataframe
    timest_format
        (If provided) Format of the timestamp columns in the CSV file
    timest_columns
        Columns of the CSV that shall be converted into timestamp

    Returns
    ------------
    df
        Dataframe with timestamp columns converted

    """
    needs_conversion = check_pandas_ge_024()
    for col in df.columns:
        if timest_columns is None or col in timest_columns:
            if df[col].dtype == 'object':
                try:
                    if timest_format is None:
                        if needs_conversion:
                            df[col] = pd.to_datetime(df[col], utc=True)
                        else:
                            df[col] = pd.to_datetime(df[col])
                    else:
                        if needs_conversion:
                            df[col] = pd.to_datetime(df[col], utc=True, format=timest_format)
                        else:
                            df[col] = pd.to_datetime(df[col])
                except ValueError:
                    # print("exception converting column: "+str(col))
                    pass
    return df


def import_dataframe_from_path(path, sep=',', quotechar=None, nrows=None, sort=False, sort_field="time:timestamp",
                               timest_format=None, timest_columns=None):
    """
    Imports a dataframe from the given path

    Parameters
    ----------
    path:
        Input CSV file path
    sep:
        column separator
    quotechar
        (if specified) Character that starts/end big strings in CSV
    nrows
        (if specified) Maximum number of rows to read from the CSV
    sort
        Boolean value that tells if the CSV should be ordered
    sort_field
        If sort option is enabled, then the CSV is automatically sorted by the specified column
    timest_format
        (If provided) Format of the timestamp columns in the CSV file
    timest_columns
        Columns of the CSV that shall be converted into timestamp

     Returns
    -------
    pd
        Pandas dataframe
    """
    df = import_dataframe_from_path_wo_timeconversion(path, sep=sep, quotechar=quotechar, nrows=nrows)
    df = convert_timestamp_columns_in_df(df, timest_format=timest_format, timest_columns=timest_columns)
    if sort and sort_field:
        df = df.sort_values(sort_field)
    return df

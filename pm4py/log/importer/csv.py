from pm4py import log
import pandas as pd
import tempfile, os

def import_dataframe_from_csv_string(csv_string, sep=',', quotechar=None, nrows=None, sort=False, sort_field=None):
    """
    Import dataframe from CSV string

    Parameters
    -----------
    csv_string
        CSV string

    Returns
    -----------
    df
        Pandas dataframe
    """
    fp = tempfile.NamedTemporaryFile(suffix='.csv')
    fp.close()
    with open(fp.name, 'w') as f:
        f.write(csv_string)
    df = import_dataframe_from_path(fp.name, sep=sep, quotechar=quotechar, nrows=nrows, sort=sort, sort_field=sort_field)
    os.remove(fp.name)
    return df

def import_from_csv_string(csv_string, sep=',', quotechar=None, nrows=None, sort=False, sort_field=None):
    """
    Import CSV log from CSV string

    Parameters
    -----------
    csv_string
        CSV string

    Returns
    -----------
    log
        Event log
    """
    fp = tempfile.NamedTemporaryFile(suffix='.csv')
    fp.close()
    with open(fp.name, 'w') as f:
        f.write(csv_string)
    log = import_from_path(fp.name, sep=sep, quotechar=quotechar, nrows=nrows, sort=sort, sort_field=sort_field)
    os.remove(fp.name)
    return log

def import_dataframe_from_path_wo_timeconversion(path, sep=',', quotechar=None, nrows=None):
    """
    Imports a dataframe from the given path (without doing the timestamp columns conversion)

    Parameters
    ----------
    path:
        Input CSV file path
    sep:
        column separator

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

def convert_timestamp_columns_in_df(df):
    """
    Convert all dataframe columns in a dataframe

    Parameters
    -----------
    df
        Dataframe

    Returns
    ------------
    df
        Dataframe with timestamp columns converted
    """
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                df[col] = pd.to_datetime(df[col])
            except ValueError:
                    pass
    return df

def import_dataframe_from_path(path, sep=',', quotechar=None, nrows=None, sort=False, sort_field=None):
    """
    Imports a dataframe from the given path

    Parameters
    ----------
    path:
        Input CSV file path
    sep:
        column separator

     Returns
    -------
    pd
        Pandas dataframe
    """
    df = import_dataframe_from_path_wo_timeconversion(path, sep=sep, quotechar=quotechar, nrows=nrows)
    df = convert_timestamp_columns_in_df(df)
    if sort and sort_field:
        df = df.sort_values(sort_field)
    return df

def convert_dataframe_to_event_log(df):
    """
    Converts a dataframe to an event log

    Parameters
    ----------
    df
        Pandas dataframe

     Returns
    -------
    log : :class:`pm4py.log.log.EventLog`
        An event log
    """
    return log.log.EventLog(df.to_dict('records'), attributes={'origin': 'csv'})

def import_from_path(path, sep=',', quotechar=None, nrows=None, sort=False, sort_field=None):
    """
    Imports a CSV file from the given path

    Parameters
    ----------
    path:
        Input CSV file path
    sep:
        column separator

     Returns
    -------
    log : :class:`pm4py.log.log.EventLog`
        An event log
    """
    df = import_dataframe_from_path(path, sep=sep, quotechar=quotechar, nrows=nrows, sort=sort, sort_field=sort_field)
    return convert_dataframe_to_event_log(df)

from pm4py import log
import pandas as pd
import tempfile, os

def import_dataframe_from_csv_string(csv_string, sep=',', quotechar=None, nrows=None):
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
    df = import_dataframe_from_path(fp.name, sep=sep, quotechar=quotechar, nrows=nrows)
    os.remove(fp.name)
    return df

def import_from_csv_string(csv_string, sep=',', quotechar=None, nrows=None):
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
    log = import_from_path(fp.name, sep=sep, quotechar=quotechar, nrows=nrows)
    os.remove(fp.name)
    return log

def import_dataframe_from_path(path, sep=',', quotechar=None, nrows=None):
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
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                df[col] = pd.to_datetime(df[col])
            except ValueError:
                    pass
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
    return log.instance.EventLog(df.to_dict('records'), attributes={'origin': 'csv'})

def import_from_path(path, sep=',', quotechar=None, nrows=None):
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
    df = import_dataframe_from_path(path, sep=sep, quotechar=quotechar, nrows=nrows)
    return convert_dataframe_to_event_log(df)

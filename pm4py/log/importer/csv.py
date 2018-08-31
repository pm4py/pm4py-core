from pm4py import log
import pandas as pd
import tempfile, os

def import_from_csv_string(csv_string, sep=','):
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
    log = import_from_path(fp.name, sep=',')
    os.remove(fp.name)
    return log

def import_from_path(path, sep=','):
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
    log : :class:`pm4py.log.instance.EventLog`
        An event log
    """
    df = pd.read_csv(path, sep=sep)
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                df[col] = pd.to_datetime(df[col])
            except ValueError:
                    pass
    return log.log.EventLog(df.to_dict('records'), attributes={'origin': 'csv'})

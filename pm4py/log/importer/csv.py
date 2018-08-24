from pm4py import log
import pandas as pd


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
    return log.instance.EventLog(df.to_dict('records'), attributes={'origin': 'csv'})

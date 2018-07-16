import pm4py.log.instance as log_instance
import pandas as pd


def import_from_path(path, sep=','):
    df = pd.read_csv(path, sep=sep)
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                df[col] = pd.to_datetime(df[col])
            except ValueError:
                    pass
    return log_instance.EventLog(df.to_dict('records'), attributes={'origin': 'csv'})

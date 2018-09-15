from pm4py import log
import tempfile, os
from pm4py.log.adapters.pandas.csv_import_adapter import import_dataframe_from_path

def import_from_csv_string(csv_string, sep=',', quotechar=None, nrows=None, sort=False, sort_field="time:timestamp", insert_event_indexes=False):
    """
    Import CSV log from CSV string

    Parameters
    -----------
    csv_string
        CSV string
    quotechar
        (if specified) Character that starts/end big strings in CSV
    nrows
        (if specified) Maximum number of rows to read from the CSV
    sort
        Boolean value that tells if the CSV should be ordered
    sort_field
        If sort option is enabled, then the CSV is automatically sorted by the specified column


    Returns
    -----------
    log
        Event log
    """
    fp = tempfile.NamedTemporaryFile(suffix='.csv')
    fp.close()
    with open(fp.name, 'w') as f:
        f.write(csv_string)
    log = import_from_path(fp.name, sep=sep, quotechar=quotechar, nrows=nrows, sort=sort, sort_field=sort_field, insert_event_indexes=insert_event_indexes)
    os.remove(fp.name)
    return log

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

def import_from_path(path, sep=',', quotechar=None, nrows=None, sort=False, sort_field="time:timestamp", insert_event_indexes=False):
    """
    Imports a CSV file from the given path

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

     Returns
    -------
    log : :class:`pm4py.log.log.EventLog`
        An event log
    """
    df = import_dataframe_from_path(path, sep=sep, quotechar=quotechar, nrows=nrows, sort=sort, sort_field=sort_field)
    event_log = convert_dataframe_to_event_log(df)

    if insert_event_indexes:
        event_log.insert_event_index_as_event_attribute()

    return event_log
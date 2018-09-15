from pm4py.log.importer.csv.versions import pandas_df_imp

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

    return pandas_df_imp.import_from_path(path, sep=sep, quotechar=quotechar, nrows=nrows, sort=sort, sort_field=sort_field, insert_event_indexes=insert_event_indexes)
from pm4py.objects.log.adapters.pandas.csv_import_adapter import import_dataframe_from_path
from pm4py.objects.conversion.log import factory as log_conv_fact


def import_event_stream(path, parameters=None):
    """
    Imports a CSV file from the given path

    Parameters
    ----------
    path:
        Input CSV file path
    parameters
        Parameters of the algorithm, including
            sep -> column separator
            quotechar -> (if specified) Character that starts/end big strings in CSV
            nrows -> (if specified) Maximum number of rows to read from the CSV
            sort -> Boolean value that tells if the CSV should be ordered
            sort_field -> If sort option is enabled, then the CSV is automatically sorted by the specified column

     Returns
    -------
    log : :class:`pm4py.log.log.EventLog`
        An event log
    """

    sep = ","
    quotechar = None
    nrows = None
    sort = False
    sort_field = "time:timestamp"
    insert_event_indexes = False
    timest_format = None
    timest_columns = None

    if parameters is None:
        parameters = {}
    if "sep" in parameters:
        sep = parameters["sep"]
    if "quotechar" in parameters:
        quotechar = parameters["quotechar"]
    if "nrows" in parameters:
        nrows = parameters["nrows"]
    if "sort" in parameters:
        sort = parameters["sort"]
    if "sort_field" in parameters:
        sort_field = parameters["sort_field"]
    if "insert_event_indexes" in parameters:
        insert_event_indexes = parameters["insert_event_indexes"]
    if "timest_format" in parameters:
        timest_format = parameters["timest_format"]
    if "timest_columns" in parameters:
        timest_columns = parameters["timest_columns"]

    df = import_dataframe_from_path(path, sep=sep, quotechar=quotechar, nrows=nrows, sort=sort, sort_field=sort_field,
                                    timest_format=timest_format, timest_columns=timest_columns)
    event_log = log_conv_fact.apply(df, variant=log_conv_fact.TO_EVENT_STREAM)

    if insert_event_indexes:
        event_log.insert_event_index_as_event_attribute()

    return event_log


def import_log(path, parameters=None):
    return import_event_stream(path, parameters=parameters)
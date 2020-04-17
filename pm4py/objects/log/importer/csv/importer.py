from pm4py.objects.log.adapters.pandas import csv_import_adapter as pandas_csv_import_adapter
from pm4py.objects.log.importer.csv.versions import pandas_df_imp
from pm4py.objects.log.util import string_to_file
from pm4py.util import xes_constants as xes

SEP = "sep"
QUOTECHAR = "quotechar"
NROWS = "nrows"
SORT = "sort"
SORT_FIELD = "sort_field"
TIMEST_FORMAT = "timest_format"
TIMEST_COLUMNS = "timest_columns"
INSERT_EVENT_INDEXES = "insert_event_indexes"
ENCODING = "encoding"

PANDAS = "pandas"
VERSIONS = {PANDAS: pandas_df_imp.import_event_stream}

DATAFRAME_MANAGER = {PANDAS: pandas_csv_import_adapter}


def import_dataframe_from_path(path, parameters=None, variant=PANDAS):
    """
    Imports a dataframe from the given path

    Parameters
    ----------
    path:
        Input CSV file path
    parameters
        Parameters of the importing: sep, quotechar, nrows, sort, sort_field, timest_format, timest_columns
    variant
        Variant of the dataframe manager (possible values: pandas)

     Returns
    -------
    pd
        Pandas dataframe
    """
    if parameters is None:
        parameters = {}

    sep = parameters[SEP] if SEP in parameters else ','
    quotechar = parameters[QUOTECHAR] if QUOTECHAR in parameters else None
    nrows = parameters[NROWS] if NROWS in parameters else None

    sort = parameters[SORT] if SORT in parameters else False
    sort_field = parameters[SORT_FIELD] if SORT_FIELD in parameters else xes.DEFAULT_TIMESTAMP_KEY
    timest_format = parameters[TIMEST_FORMAT] if TIMEST_FORMAT in parameters else None
    timest_columns = parameters[TIMEST_COLUMNS] if TIMEST_COLUMNS in parameters else None
    encoding = parameters[ENCODING] if ENCODING in parameters else None

    return DATAFRAME_MANAGER[variant].import_dataframe_from_path(path, sep=sep, quotechar=quotechar, nrows=nrows,
                                                                 sort=sort,
                                                                 sort_field=sort_field, timest_format=timest_format,
                                                                 timest_columns=timest_columns, encoding=encoding)


def import_dataframe_from_path_wo_timeconversion(path, parameters=None, variant=PANDAS):
    """
    Imports a dataframe from the given path (without doing the timestamp columns conversion)

    Parameters
    ----------
    path:
        Input CSV file path
    parameters
        parameters of the importing: sep, quotechar, nrows
    variant
        Variant of the dataframe manager (possible values: pandas)

     Returns
    -------
    pd
        Pandas dataframe
    """
    if parameters is None:
        parameters = {}

    sep = parameters[SEP] if SEP in parameters else ','
    quotechar = parameters[QUOTECHAR] if QUOTECHAR in parameters else None
    nrows = parameters[NROWS] if NROWS in parameters else None
    encoding = parameters[ENCODING] if ENCODING in parameters else None

    return DATAFRAME_MANAGER[variant].import_dataframe_from_path_wo_timeconversion(path, sep=sep, quotechar=quotechar,
                                                                                   nrows=nrows, encoding=encoding)


def import_dataframe_from_csv_string(csv_string, parameters=None, variant=PANDAS):
    """
    Import dataframe from CSV string

    Parameters
    -----------
    csv_string
        CSV string
    parameters
        Parameters of the importing: sep, quotechar, nrows, sort, sort_field, timest_format, timest_columns
    variant
        Variant of the dataframe manager (possible values: pandas)

    Returns
    -----------
    df
        Pandas dataframe
    """
    if parameters is None:
        parameters = {}

    sep = parameters[SEP] if SEP in parameters else ','
    quotechar = parameters[QUOTECHAR] if QUOTECHAR in parameters else None
    nrows = parameters[NROWS] if NROWS in parameters else None

    sort = parameters[SORT] if SORT in parameters else False
    sort_field = parameters[SORT_FIELD] if SORT_FIELD in parameters else xes.DEFAULT_TIMESTAMP_KEY
    timest_format = parameters[TIMEST_FORMAT] if TIMEST_FORMAT in parameters else None
    timest_columns = parameters[TIMEST_COLUMNS] if TIMEST_COLUMNS in parameters else None
    encoding = parameters[ENCODING] if ENCODING in parameters else None

    return DATAFRAME_MANAGER[variant].import_dataframe_from_csv_string(csv_string, sep=sep, quotechar=quotechar,
                                                                       nrows=nrows,
                                                                       sort=sort, sort_field=sort_field,
                                                                       timest_format=timest_format,
                                                                       timest_columns=timest_columns,
                                                                       encoding=encoding)


def convert_dataframe_to_stream(dataframe, parameters=None, variant=PANDAS):
    """
    Convert a dataframe to an event stream

    Parameters
    -------------
    dataframe
        Dataframe
    parameters
        Parameters of the conversion: insert_event_indexes
    variant
        Variant of the dataframe manager (possible values: pandas)

    Returns
    -------------
    stream
        Event stream
    """
    if parameters is None:
        parameters = {}
    
    insert_event_indexes = parameters[INSERT_EVENT_INDEXES] if INSERT_EVENT_INDEXES in parameters else False

    return DATAFRAME_MANAGER[variant].convert_dataframe_to_stream(dataframe, insert_event_indexes=insert_event_indexes)


def convert_timestamp_columns_in_df(df, timest_format=None, timest_columns=None, variant=PANDAS):
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
    variant
        Variant of the dataframe manager (possible values: pandas)

    Returns
    ------------
    df
        Dataframe with timestamp columns converted

    """
    return DATAFRAME_MANAGER[variant].convert_timestamp_columns_in_df(df, timest_format=timest_format,
                                                                      timest_columns=timest_columns)


def import_log_from_string(log_string, parameters=None, variant="pandas"):
    """
    Import a CSV log from a string

    Parameters
    -----------
    log_string
        String that contains the CSV
    parameters
        Parameters of the algorithm, including
            sep -> column separator
            quotechar -> (if specified) Character that starts/end big strings in CSV
            nrows -> (if specified) Maximum number of rows to read from the CSV
            sort -> Boolean value that tells if the CSV should be ordered
            sort_field -> If sort option is enabled, then the CSV is automatically sorted by the specified column
    variant
        Variant of the algorithm to use, including:
            pandas

    Returns
    -----------
    log
        Event log object
    """
    temp_file = string_to_file.import_string_to_temp_file(log_string, "csv")
    return import_event_stream(temp_file, parameters=parameters, variant=variant)


def import_event_stream(path, parameters=None, variant="pandas"):
    """
    Import a CSV log into an EventLog object

    Parameters
    -----------
    path
        Log path
    parameters
        Parameters of the algorithm, including
            sep -> column separator
            quotechar -> (if specified) Character that starts/end big strings in CSV
            nrows -> (if specified) Maximum number of rows to read from the CSV
            sort -> Boolean value that tells if the CSV should be ordered
            sort_field -> If sort option is enabled, then the CSV is automatically sorted by the specified column
    variant
        Variant of the algorithm to use, including:
            pandas

    Returns
    -----------
    log
        Event log object
    """
    return VERSIONS[variant](path, parameters=parameters)


def import_event_log(path, parameters=None, variant="pandas"):
    # legacy method, to be removed
    return import_event_stream(path, parameters=parameters, variant="pandas")


def apply(path, parameters=None, variant="pandas"):
    """
    Import a CSV log into an EventLog object

    Parameters
    -----------
    path
        Log path
    parameters
        Parameters of the algorithm, including
            sep -> column separator
            quotechar -> (if specified) Character that starts/end big strings in CSV
            nrows -> (if specified) Maximum number of rows to read from the CSV
            sort -> Boolean value that tells if the CSV should be ordered
            sort_field -> If sort option is enabled, then the CSV is automatically sorted by the specified column
    variant
        Variant of the algorithm to use, including:
            pandas

    Returns
    -----------
    log
        Event log object
    """
    return import_event_stream(path, parameters=parameters, variant=variant)

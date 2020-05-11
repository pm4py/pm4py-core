import deprecation

from pm4py.objects.log.adapters.pandas import csv_import_adapter as pandas_csv_import_adapter
from pm4py.objects.log.util import string_to_file
from enum import Enum
from pm4py.util import exec_utils, xes_constants
from pm4py.objects.log.importer.csv.parameters import Parameters


class Variants(Enum):
    PANDAS = pandas_csv_import_adapter


PANDAS = Variants.PANDAS
VERSIONS = {PANDAS}


@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Please import the csv using pandas, then convert it to an event log, if needed')
def import_dataframe_from_path(path, parameters=None, variant=PANDAS):
    """
    Imports a dataframe from the given path

    Parameters
    ----------
    path:
        Input CSV file path
    parameters
        Parameters of the importing:
            - Parameters.SEP
            - Parameters.QUOTECHAR
            - Parameters.NROWS
            - Parameters.SORT
            - Parameters.SORT_FIELD
            - Parameters.TIMEST_FORMAT
            - Parameters.TIMEST_COLUMNS
            - Parameters.ENCODING
    variant
        Variant of the dataframe manager:
            - Variants.PANDAS

     Returns
    -------
    pd
        Pandas dataframe
    """
    if parameters is None:
        parameters = {}

    sep = exec_utils.get_param_value(Parameters.SEP, parameters, ",")
    quotechar = exec_utils.get_param_value(Parameters.QUOTECHAR, parameters, None)
    nrows = exec_utils.get_param_value(Parameters.NROWS, parameters, None)
    sort = exec_utils.get_param_value(Parameters.SORT, parameters, False)
    sort_field = exec_utils.get_param_value(Parameters.SORT_FIELD, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)
    timest_format = exec_utils.get_param_value(Parameters.TIMEST_FORMAT, parameters, None)
    timest_columns = exec_utils.get_param_value(Parameters.TIMEST_COLUMNS, parameters, None)
    encoding = exec_utils.get_param_value(Parameters.ENCODING, parameters, None)

    return exec_utils.get_variant(variant).import_dataframe_from_path(path, sep=sep, quotechar=quotechar, nrows=nrows,
                                                                      sort=sort,
                                                                      sort_field=sort_field,
                                                                      timest_format=timest_format,
                                                                      timest_columns=timest_columns, encoding=encoding)


@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Please import the csv using pandas, then convert it to an event log, if needed')
def import_dataframe_from_path_wo_timeconversion(path, parameters=None, variant=PANDAS):
    """
    Imports a dataframe from the given path (without doing the timestamp columns conversion)

    Parameters
    ----------
    path:
        Input CSV file path
    parameters
        Parameters of the importing:
            - Parameters.SEP
            - Parameters.QUOTECHAR
            - Parameters.NROWS
            - Parameters.ENCODING
    variant
        Variant of the dataframe manager:
            - Variants.PANDAS

     Returns
    -------
    pd
        Pandas dataframe
    """
    if parameters is None:
        parameters = {}

    sep = exec_utils.get_param_value(Parameters.SEP, parameters, ",")
    quotechar = exec_utils.get_param_value(Parameters.QUOTECHAR, parameters, None)
    nrows = exec_utils.get_param_value(Parameters.NROWS, parameters, None)
    encoding = exec_utils.get_param_value(Parameters.ENCODING, parameters, None)

    return exec_utils.get_variant(variant).import_dataframe_from_path_wo_timeconversion(path, sep=sep,
                                                                                        quotechar=quotechar,
                                                                                        nrows=nrows, encoding=encoding)


@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Please import the csv using pandas, then convert it to an event log, if needed')
def import_dataframe_from_csv_string(csv_string, parameters=None, variant=PANDAS):
    """
    Import dataframe from CSV string

    Parameters
    -----------
    csv_string
        CSV string
    parameters
        Parameters of the importing:
            - Parameters.SEP
            - Parameters.QUOTECHAR
            - Parameters.NROWS
            - Parameters.SORT
            - Parameters.SORT_FIELD
            - Parameters.TIMEST_FORMAT
            - Parameters.TIMEST_COLUMNS
            - Parameters.ENCODING
    variant
        Variant of the dataframe manager:
            - Variants.PANDAS

    Returns
    -----------
    df
        Pandas dataframe
    """
    if parameters is None:
        parameters = {}

    sep = exec_utils.get_param_value(Parameters.SEP, parameters, ",")
    quotechar = exec_utils.get_param_value(Parameters.QUOTECHAR, parameters, None)
    nrows = exec_utils.get_param_value(Parameters.NROWS, parameters, None)
    sort = exec_utils.get_param_value(Parameters.SORT, parameters, False)
    sort_field = exec_utils.get_param_value(Parameters.SORT_FIELD, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)
    timest_format = exec_utils.get_param_value(Parameters.TIMEST_FORMAT, parameters, None)
    timest_columns = exec_utils.get_param_value(Parameters.TIMEST_COLUMNS, parameters, None)
    encoding = exec_utils.get_param_value(Parameters.ENCODING, parameters, None)

    return exec_utils.get_variant(variant).import_dataframe_from_csv_string(csv_string, sep=sep, quotechar=quotechar,
                                                                            nrows=nrows,
                                                                            sort=sort, sort_field=sort_field,
                                                                            timest_format=timest_format,
                                                                            timest_columns=timest_columns,
                                                                            encoding=encoding)


@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Please import the csv using pandas, then convert it to an event log, if needed')
def convert_dataframe_to_stream(dataframe, parameters=None, variant=PANDAS):
    """
    Convert a dataframe to an event stream

    Parameters
    -------------
    dataframe
        Dataframe
    parameters
        Parameters of the importing:
            - Parameters.INSERT_EVENT_INDEXES
    variant
        Variant of the dataframe manager:
            - Variants.PANDAS

    Returns
    -------------
    stream
        Event stream
    """
    if parameters is None:
        parameters = {}

    insert_event_indexes = exec_utils.get_param_value(Parameters.INSERT_EVENT_INDEXES, parameters, False)

    return exec_utils.get_variant(variant).convert_dataframe_to_stream(dataframe,
                                                                       insert_event_indexes=insert_event_indexes)


@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Please import the csv using pandas, then convert it to an event log, if needed')
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
    return exec_utils.get_variant(variant).convert_timestamp_columns_in_df(df, timest_format=timest_format,
                                                                           timest_columns=timest_columns)


@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Please import the csv using pandas, then convert it to an event log, if needed')
def import_log_from_string(log_string, parameters=None, variant=PANDAS):
    """
    Import a CSV log from a string

    Parameters
    -----------
    log_string
        String that contains the CSV
    parameters
        Parameters of the importing:
            - Parameters.SEP
            - Parameters.QUOTECHAR
            - Parameters.NROWS
            - Parameters.SORT
            - Parameters.SORT_FIELD
            - Parameters.TIMEST_FORMAT
            - Parameters.TIMEST_COLUMNS
            - Parameters.ENCODING
    variant
        Variant of the dataframe manager:
            - Variants.PANDAS

    Returns
    -----------
    log
        Event log object
    """
    temp_file = string_to_file.import_string_to_temp_file(log_string, "csv")
    return import_event_stream(temp_file, parameters=parameters, variant=variant)


@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Please import the csv using pandas, then convert it to an event log, if needed')
def import_event_stream(path, parameters=None, variant=PANDAS):
    """
    Import a CSV log into an EventLog object

    Parameters
    -----------
    path
        Log path
    parameters
        Parameters of the importing:
            - Parameters.SEP
            - Parameters.QUOTECHAR
            - Parameters.NROWS
            - Parameters.SORT
            - Parameters.SORT_FIELD
            - Parameters.TIMEST_FORMAT
            - Parameters.TIMEST_COLUMNS
            - Parameters.ENCODING
    variant
        Variant of the dataframe manager:
            - Variants.PANDAS

    Returns
    -----------
    log
        Event log object
    """
    dataframe = import_dataframe_from_path(path, variant=variant, parameters=parameters)
    return convert_dataframe_to_stream(dataframe, variant=variant, parameters=parameters)


@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Please import the csv using pandas, then convert it to an event log, if needed')
def import_event_log(path, parameters=None, variant=PANDAS):
    # legacy method, to be removed
    return import_event_stream(path, parameters=parameters, variant=variant)


@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Please import the csv using pandas, then convert it to an event log, if needed')
def apply(path, parameters=None, variant=PANDAS):
    """
    Import a CSV log into an EventLog object

    Parameters
    -----------
    path
        Log path
    parameters
        Parameters of the importing:
            - Parameters.SEP
            - Parameters.QUOTECHAR
            - Parameters.NROWS
            - Parameters.SORT
            - Parameters.SORT_FIELD
            - Parameters.TIMEST_FORMAT
            - Parameters.TIMEST_COLUMNS
            - Parameters.ENCODING
    variant
        Variant of the dataframe manager:
            - Variants.PANDAS

    Returns
    -----------
    log
        Event log object
    """
    return import_event_stream(path, parameters=parameters, variant=variant)

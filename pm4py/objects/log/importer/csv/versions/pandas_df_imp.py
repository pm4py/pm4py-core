from pm4py.objects.log.adapters.pandas.csv_import_adapter import import_dataframe_from_path
from pm4py.objects.conversion.log import converter as log_conv_fact
from pm4py.objects.log.importer.csv.parameters import Parameters
import deprecation
from pm4py.util import exec_utils


@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Please import the csv using pandas, then convert it to an event log, if needed')
def import_event_stream(path, parameters=None):
    """
    Imports a CSV file from the given path

    Parameters
    ----------
    path:
        Input CSV file path
    parameters
        Parameters of the algorithm, including
            Parameters.SEPARATOR -> column separator
            Parameters.QUOTECHAR -> (if specified) Character that starts/end big strings in CSV
            Parameters.NUM_ROWS -> (if specified) Maximum number of rows to read from the CSV
            Parameters.SORT -> Boolean value that tells if the CSV should be ordered
            Parameters.SORT_FIELD -> If sort option is enabled, then the CSV is automatically sorted by the specified column
            Parameters.INSERT_EVENT_INDICES -> Events get their index as an additional payload
            Parameters.TIME_STAMP_FORMAT -> Specify the timestamp format, if not specified, auto detection is applied
            Parameters.TIME_STAMP_COLUMNS -> Column names of data attributes that contain time stamps
            Parameters.ENCODING -> File Encoding

     Returns
    -------
    log : :class:`pm4py.log.log.EventLog`
        An event log
    """
    parameters = {} if parameters is None else parameters
    insert_event_indexes = exec_utils.get_param_value(Parameters.INSERT_EVENT_INDEXES, parameters, False)
    df = import_dataframe_from_path(path, sep=exec_utils.get_param_value(Parameters.SEP, parameters, ","),
                                    quotechar=exec_utils.get_param_value(Parameters.QUOTECHAR, parameters, None),
                                    nrows=exec_utils.get_param_value(Parameters.NROWS, parameters, None),
                                    sort=exec_utils.get_param_value(Parameters.SORT, parameters, False),
                                    sort_field=exec_utils.get_param_value(Parameters.SORT_FIELD, parameters, 'time:timestamp'),
                                    timest_format=exec_utils.get_param_value(Parameters.TIMEST_FORMAT, parameters, None),
                                    timest_columns=exec_utils.get_param_value(Parameters.TIMEST_COLUMNS, parameters, None),
                                    encoding=exec_utils.get_param_value(Parameters.ENCODING, parameters, None))
    stream = log_conv_fact.apply(df, variant=log_conv_fact.TO_EVENT_STREAM)

    if insert_event_indexes:
        stream.insert_event_index_as_event_attribute()
    return stream


@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Please import the csv using pandas, then convert it to an event log, if needed')
def import_log(path, parameters=None):
    return import_event_stream(path, parameters=parameters)

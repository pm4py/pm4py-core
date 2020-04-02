import pyarrow
from pm4py.objects.log.serialization.versions import parquet_dataframe, pyarrow_event_stream, pyarrow_event_log
from pm4py.objects.log.log import EventLog, EventStream
import pandas as pd

PYARROW_EVENT_STREAM="pyarrow_event_stream"
PYARROW_EVENT_LOG="pyarrow_event_log"
PARQUET_DATAFRAME="parquet_dataframe"

DEFAULT_EVENT_STREAM=PYARROW_EVENT_STREAM
DEFAULT_EVENT_LOG=PYARROW_EVENT_LOG
DEFAULT_DATAFRAME=PARQUET_DATAFRAME


VERSIONS_APPLY_EVENT_STREAM={PYARROW_EVENT_STREAM: pyarrow_event_stream.apply}
VERSIONS_APPLY_EVENT_LOG={PYARROW_EVENT_LOG: pyarrow_event_log.apply}
VERSIONS_APPLY_DATAFRAME={PARQUET_DATAFRAME: parquet_dataframe.apply}

VERSIONS_EXPORT_FILE_EVENT_STREAM={PYARROW_EVENT_STREAM: pyarrow_event_stream.export_to_file}
VERSIONS_EXPORT_FILE_EVENT_LOG={PYARROW_EVENT_LOG: pyarrow_event_log.export_to_file}
VERSIONS_EXPORT_FILE_DATAFRAME={PARQUET_DATAFRAME: parquet_dataframe.export_to_file}


def apply(log, variant=None, parameters=None):
    """
    Serialize a log object to Pyarrow bytes

    Parameters
    --------------
    log
        Event log
    variant
        Variant of the algorithm, possible values: pyarrow_event_stream, pyarrow_event_log, parquet_dataframe
    parameters
        Possible parameters of the algorithm

    Returns
    --------------
    serialization
        Serialized bytes
    """
    if type(log) is EventLog:
        if variant is None:
            variant=DEFAULT_EVENT_LOG
        return VERSIONS_APPLY_EVENT_LOG[variant](log, parameters=parameters)
    elif type(log) is EventStream:
        if variant is None:
            variant=DEFAULT_EVENT_STREAM
        return VERSIONS_APPLY_EVENT_STREAM[variant](log, parameters=parameters)
    elif type(log) is pd.DataFrame:
        if variant is None:
            variant=DEFAULT_DATAFRAME
        return VERSIONS_APPLY_DATAFRAME[variant](log, parameters=parameters)


def export_to_file(log, file_path, variant=None, parameters=None):
    """
    Serialize a log object to the content of a file

    Parameters
    --------------
    log
        Event log
    file_path
        File path  (if None, then a temp file is targeted)
    variant
        Variant of the algorithm, possible values: pyarrow_event_stream, pyarrow_event_log, parquet_dataframe
    parameters
        Possible parameters of the algorithm

    Returns
    --------------
    file_path
        File path
    """
    if type(log) is EventLog:
        if variant is None:
            variant=DEFAULT_EVENT_LOG
        return VERSIONS_EXPORT_FILE_EVENT_LOG[variant](log, file_path, parameters=parameters)
    elif type(log) is EventStream:
        if variant is None:
            variant=DEFAULT_EVENT_STREAM
        return VERSIONS_EXPORT_FILE_EVENT_STREAM[variant](log, file_path, parameters=parameters)
    elif type(log) is pd.DataFrame:
        if variant is None:
            variant=DEFAULT_DATAFRAME
        return VERSIONS_EXPORT_FILE_DATAFRAME[variant](log, file_path, parameters=parameters)

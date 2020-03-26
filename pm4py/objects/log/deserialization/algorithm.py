import pyarrow
from pm4py.objects.log.deserialization.versions import parquet_dataframe, pyarrow_event_log, pyarrow_event_stream
from pm4py.objects.log.log import EventLog, EventStream
import pandas as pd


PYARROW_EVENT_STREAM="pyarrow_event_stream"
PYARROW_EVENT_LOG="pyarrow_event_log"
PARQUET_DATAFRAME="parquet_dataframe"

DEFAULT_EVENT_STREAM=PYARROW_EVENT_STREAM
DEFAULT_EVENT_LOG=PYARROW_EVENT_LOG
DEFAULT_DATAFRAME=PARQUET_DATAFRAME


VERSIONS_APPLY={PYARROW_EVENT_STREAM: pyarrow_event_stream.apply, PYARROW_EVENT_LOG: pyarrow_event_log.apply, PARQUET_DATAFRAME: parquet_dataframe.apply}

VERSIONS_IMPORT_FILE={PYARROW_EVENT_STREAM: pyarrow_event_stream.import_from_file, PYARROW_EVENT_LOG: pyarrow_event_log.import_from_file, PARQUET_DATAFRAME: parquet_dataframe.import_from_file}


def apply(bytes, variant, parameters=None):
    """
    Apply the deserialization to the bytes produced by Pyarrow serialization

    Parameters
    --------------
    bytes
        Bytes
    variant
        Deserialization variant that MUST be specified (values: pyarrow_event_stream, pyarrow_event_log, parquet_dataframe)
    parameters
        Parameters of the algorithm

    Returns
    --------------
    deser
        Deserialized object
    """
    return VERSIONS_APPLY[variant](bytes, parameters=parameters)


def import_from_file(file_path, variant, parameters=None):
    """
    Apply the deserialization to a file produced by Pyarrow serialization

    Parameters
    --------------
    file_path
        File path
    variant
        Deserialization variant that MUST be specified (values: pyarrow_event_stream, pyarrow_event_log, parquet_dataframe)
    parameters
        Parameters of the algorithm

    Returns
    --------------
    deser
        Deserialized object
    """
    return VERSIONS_IMPORT_FILE[variant](file_path, parameters=parameters)

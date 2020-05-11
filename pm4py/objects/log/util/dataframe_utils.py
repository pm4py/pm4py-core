from pm4py.util import constants
from pm4py.objects.log.log import EventStream
from pm4py.objects.conversion.log import converter as log_converter
import pandas as pd
from pm4py.util.versions import check_pandas_ge_024

COLUMNS = "columns"
LEGACY_PARQUET_TP_REPLACER = "AAA"
LEGACY_PARQUET_CASECONCEPTNAME = "caseAAAconceptAAAname"


def insert_partitioning(df, num_partitions, parameters=None):
    """
    Insert the partitioning in the specified dataframe

    Parameters
    -------------
    df
        Dataframe
    num_partitions
        Number of partitions
    parameters
        Parameters of the algorithm

    Returns
    -------------
    df
        Partitioned dataframe
    """
    if parameters is None:
        parameters = {}

    case_id_key = parameters[
        constants.PARAMETER_CONSTANT_CASEID_KEY] if constants.PARAMETER_CONSTANT_CASEID_KEY in parameters else constants.CASE_CONCEPT_NAME
    partition_column = parameters["partition_column"] if "partition_column" in parameters else "@@partitioning"

    df[partition_column] = df[case_id_key].rank(method='dense', ascending=False).astype(int) % num_partitions

    return df


def legacy_parquet_support(df, parameters=None):
    """
    For legacy support, Parquet files columns could not contain
    a ":" that has been arbitrarily replaced by a replacer string.
    This string substitutes the replacer to the :

    Parameters
    ---------------
    dataframe
        Dataframe
    parameters
        Parameters of the algorithm
    """
    if parameters is None:
        parameters = {}

    df.columns = [x.replace(LEGACY_PARQUET_TP_REPLACER, ":") for x in df.columns]

    return df


def table_to_stream(table, parameters=None):
    """
    Converts a Pyarrow table to an event stream

    Parameters
    ------------
    table
        Pyarrow table
    parameters
        Possible parameters of the algorithm
    """
    if parameters is None:
        parameters = {}

    dict0 = table.to_pydict()
    keys = list(dict0.keys())
    # for legacy format support
    if LEGACY_PARQUET_CASECONCEPTNAME in keys:
        for key in keys:
            dict0[key.replace(LEGACY_PARQUET_TP_REPLACER, ":")] = dict0.pop(key)

    stream = EventStream([dict(zip(dict0, i)) for i in zip(*dict0.values())])

    return stream


def table_to_log(table, parameters=None):
    """
    Converts a Pyarrow table to an event log

    Parameters
    ------------
    table
        Pyarrow table
    parameters
        Possible parameters of the algorithm
    """
    if parameters is None:
        parameters = {}

    stream = table_to_stream(table, parameters=parameters)

    return log_converter.apply(stream, parameters=parameters)


def convert_timestamp_columns_in_df(df, timest_format=None, timest_columns=None):
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

    Returns
    ------------
    df
        Dataframe with timestamp columns converted

    """
    needs_conversion = check_pandas_ge_024()
    for col in df.columns:
        if timest_columns is None or col in timest_columns:
            if df[col].dtype == 'object':
                try:
                    if timest_format is None:
                        if needs_conversion:
                            df[col] = pd.to_datetime(df[col], utc=True)
                        else:
                            df[col] = pd.to_datetime(df[col])
                    else:
                        if needs_conversion:
                            df[col] = pd.to_datetime(df[col], utc=True, format=timest_format)
                        else:
                            df[col] = pd.to_datetime(df[col])
                except ValueError:
                    # print("exception converting column: "+str(col))
                    pass
    return df

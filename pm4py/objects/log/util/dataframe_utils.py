from pm4py.util import constants
from pm4py.algo.filtering.common.filtering_constants import CASE_CONCEPT_NAME
from pm4py.objects.log.log import EventStream, Event
from pm4py.objects.conversion.log import factory as log_conv_factory


COLUMNS = "columns"

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
        constants.PARAMETER_CONSTANT_CASEID_KEY] if constants.PARAMETER_CONSTANT_CASEID_KEY in parameters else CASE_CONCEPT_NAME
    partition_column = parameters["partition_column"] if "partition_column" in parameters else "@@partitioning"

    df[partition_column] = df[case_id_key].rank(method='dense', ascending=False).astype(int) % num_partitions

    return df


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

    columns = parameters[COLUMNS] if COLUMNS in parameters else None
    columns = [x.replace(":", "AAA") for x in columns]

    dict0 = table.to_pydict()
    N = len(dict0[list(dict0.keys())[0]])
    keys = columns if columns is not None else dict0.keys()

    stream = EventStream()
    for i in range(N):
        stream.append(Event())
    for key in keys:
        mapped_key = key.replace("AAA", ":")
        values = dict0[key]
        for i in range(N):
            if values[i] is not None:
                stream[i][mapped_key] = values[i]

    return log_conv_factory.apply(stream, parameters=parameters)

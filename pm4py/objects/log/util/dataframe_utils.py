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

    dict0 = table.to_pydict()
    keys = list(dict0.keys())
    for key in keys:
        dict0[key.replace("AAA", ":")] = dict0.pop(key)

    stream = EventStream([dict(zip(dict0, i)) for i in zip(*dict0.values())])

    return log_conv_factory.apply(stream, parameters=parameters)

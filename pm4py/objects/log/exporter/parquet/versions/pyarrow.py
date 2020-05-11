import pyarrow as pa
import pyarrow.parquet as pq
import os
import shutil
from pm4py.objects.log.util import dataframe_utils
from enum import Enum
from pm4py.util import exec_utils


class Parameters(Enum):
    COMPRESSION = "compression"
    PARTITION_COLS = "partition_cols"
    AUTO_PARTITIONING = "auto_partitioning"
    NUM_PARTITIONS = "num_partitions"


def apply(df, path, parameters=None):
    """
    Exports a dataframe to a Parquet file

    Parameters
    ------------
    df
        Dataframe
    path
        Path
    parameters
        Possible parameters of the algorithm:
            - Parameters.COMPRESSION
            - Parameters.PARTITION_COLS
            - Parameters.AUTO_PARTITIONING
            - Parameters.NUM_PARTITIONS
    """
    if parameters is None:
        parameters = {}

    compression = exec_utils.get_param_value(Parameters.COMPRESSION, parameters, "snappy")
    partition_cols = exec_utils.get_param_value(Parameters.PARTITION_COLS, parameters, None)
    auto_partitioning = exec_utils.get_param_value(Parameters.AUTO_PARTITIONING, parameters, False)
    num_partitions = exec_utils.get_param_value(Parameters.NUM_PARTITIONS, parameters, 128)

    if partition_cols is None and auto_partitioning:
        df = dataframe_utils.insert_partitioning(df, num_partitions, parameters=parameters)
        partition_cols = ["@@partitioning"]

    df = pa.Table.from_pandas(df)

    if partition_cols is not None:
        if os.path.exists(path):
            shutil.rmtree(path)
        os.mkdir(path)
        pq.write_to_dataset(df, path, compression=compression, partition_cols=partition_cols)
    else:
        pq.write_table(df, path, compression=compression)

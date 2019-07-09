import pyarrow as pa
import pyarrow.parquet as pq
import os
import shutil
from pm4py.util import constants
from pm4py.objects.log.util import xes
from pm4py.algo.filtering.common.filtering_constants import CASE_CONCEPT_NAME


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
        Possible parameters of the algorithm
    """
    if parameters is None:
        parameters = {}

    case_id_key = parameters[
        constants.PARAMETER_CONSTANT_CASEID_KEY] if constants.PARAMETER_CONSTANT_CASEID_KEY in parameters else CASE_CONCEPT_NAME

    compression = parameters["compression"] if "compression" in parameters else "snappy"
    partition_cols = parameters["partition_cols"] if "partition_cols" in parameters else None
    auto_partitioning = parameters["auto_partitioning"] if "auto_partitioning" in parameters else False
    num_partitions = parameters["num_partitions"] if "num_partitions" in parameters else 128

    if partition_cols is None and auto_partitioning:
        df["@@partitioning"] = df[case_id_key].rank(method='dense', ascending=False).astype(int) % num_partitions
        partition_cols = ["@@partitioning"]

    df.columns = [x.replace(":", "AAA") for x in df.columns]
    if partition_cols is not None:
        partition_cols = [x.replace(":", "AAA") for x in partition_cols]

    df = pa.Table.from_pandas(df)

    if partition_cols is not None:
        if os.path.exists(path):
            shutil.rmtree(path)
        os.mkdir(path)
        pq.write_to_dataset(df, path, compression=compression, partition_cols=partition_cols)
    else:
        pq.write_table(df, path, compression=compression)

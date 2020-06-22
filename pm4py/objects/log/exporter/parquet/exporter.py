import pandas

from pm4py.objects.conversion.log.versions import to_dataframe
from pm4py.objects.log.exporter.parquet.versions import pandas as pandas_exporter
from enum import Enum
from pm4py.util import exec_utils


DEFAULT_VARIANT = pandas_exporter


class Variants(Enum):
    PANDAS = pandas_exporter


try:
    from pm4py.objects.log.exporter.parquet.versions import pyarrow

    # enums cannot be changed
    class Variants(Enum):
        PANDAS = pandas_exporter
        PYARROW = pyarrow
except:
    # pyarrow is not installed correctly or does not work
    pass


def apply(log, path, parameters=None, variant=DEFAULT_VARIANT):
    """
    Exports a log to a Parquet file

    Parameters
    ------------
    log
        Log
    path
        Path
    parameters
        Possible parameters of the algorithm
    variant
        Variant of the algorithm, possible values:
            - Variants.PYARROW
            - Variants.PANDAS
    """
    if not type(log) is pandas.core.frame.DataFrame:
        log = to_dataframe.apply(log)

    return exec_utils.get_variant(variant).apply(log, path, parameters=parameters)


def export_log(log, path, parameters=None, variant=DEFAULT_VARIANT):
    """
    Exports a log to a Parquet file

    Parameters
    ------------
    log
        Log
    path
        Path
    parameters
        Possible parameters of the algorithm
    variant
        Variant of the algorithm, possible values:
            - Variants.PYARROW
            - Variants.PANDAS
    """
    if not type(log) is pandas.core.frame.DataFrame:
        log = to_dataframe.apply(log)

    return exec_utils.get_variant(variant).apply(log, path, parameters=parameters)


def export_df(log, path, parameters=None, variant=DEFAULT_VARIANT):
    """
    Exports a log to a Parquet file

    Parameters
    ------------
    log
        Log
    path
        Path
    parameters
        Possible parameters of the algorithm
    variant
        Variant of the algorithm, possible values:
            - Variants.PYARROW
            - Variants.PANDAS
    """
    if not type(log) is pandas.core.frame.DataFrame:
        log = to_dataframe.apply(log)

    return exec_utils.get_variant(variant).apply(log, path, parameters=parameters)

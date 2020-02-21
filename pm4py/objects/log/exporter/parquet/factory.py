import pandas

from pm4py.objects.conversion.log.versions import to_dataframe
from pm4py.objects.log.exporter.parquet.versions import pandas as pandas_exporter

PYARROW = "pyarrow"
PANDAS = "pandas"

DEFAULT_VARIANT = PANDAS

VERSIONS = {PANDAS: pandas_exporter.apply}

try:
    from pm4py.objects.log.exporter.parquet.versions import pyarrow
    VERSIONS[PYARROW] = pyarrow.apply

    DEFAULT_VARIANT = PYARROW
except:
    # Fastparquet is not installed
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
        Variant of the algorithm, possible values: pyarrow
    """
    if not type(log) is pandas.core.frame.DataFrame:
        log = to_dataframe.apply(log)

    return VERSIONS[variant](log, path, parameters=parameters)


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
        Variant of the algorithm, possible values: pyarrow
    """
    if not type(log) is pandas.core.frame.DataFrame:
        log = to_dataframe.apply(log)

    return VERSIONS[variant](log, path, parameters=parameters)


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
        Variant of the algorithm, possible values: pyarrow
    """
    if not type(log) is pandas.core.frame.DataFrame:
        log = to_dataframe.apply(log)

    return VERSIONS[variant](log, path, parameters=parameters)

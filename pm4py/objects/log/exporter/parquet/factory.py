import pandas

from pm4py.objects.conversion.log.versions import to_dataframe
from pm4py.objects.log.exporter.parquet.versions import pyarrow


PYARROW = "pyarrow"

VERSIONS = {PYARROW: pyarrow.apply}


def apply(log, path, parameters=None, variant=PYARROW):
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


def export_log(log, path, parameters=None, variant=PYARROW):
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


def export_df(log, path, parameters=None, variant=PYARROW):
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
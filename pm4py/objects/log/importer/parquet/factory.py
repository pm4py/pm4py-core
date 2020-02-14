import os
import pandas as pd
from pm4py.util import constants
from pm4py.util import xes_constants as xes

PYARROW = "pyarrow"
FASTPARQUET = "fastparquet"

VERSIONS = {}
VERSIONS_LOG = {}

DEFAULT_VARIANT = None
DEFAULT_VARIANT_LOG = None

try:
    from pm4py.objects.log.importer.parquet.versions import fastparquet
    VERSIONS[FASTPARQUET] = fastparquet.apply

    DEFAULT_VARIANT = FASTPARQUET
except:
    # Fastparquet is not installed
    pass

try:
    from pm4py.objects.log.importer.parquet.versions import pyarrow
    VERSIONS[PYARROW] = pyarrow.apply
    VERSIONS_LOG[PYARROW] = pyarrow.import_log

    DEFAULT_VARIANT = PYARROW
    DEFAULT_VARIANT_LOG = PYARROW
except:
    # Pyarrow is not installed
    pass

COLUMNS = "columns"


def apply(path, parameters=None, variant=DEFAULT_VARIANT):
    """
    Import a Parquet file

    Parameters
    -------------
    path
        Path of the file to import
    parameters
        Parameters of the algorithm, possible values:
            columns -> columns to import from the Parquet file
    variant
        Variant of the algorithm, possible values: pyarrow

    Returns
    -------------
    df
        Pandas dataframe
    """
    if parameters is None:
        parameters = {}

    timestamp_key = parameters[
        constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] if constants.PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else xes.DEFAULT_TIMESTAMP_KEY
    case_id_key = parameters[
        constants.PARAMETER_CONSTANT_CASEID_KEY] if constants.PARAMETER_CONSTANT_CASEID_KEY in parameters else constants.CASE_CONCEPT_NAME

    if os.path.isdir(path):
        all_parquets = get_list_parquet(path, parameters=parameters)
        dataframes = []
        for file in all_parquets:
            dataframes.append(VERSIONS[variant](file, parameters=parameters))
        df = pd.concat(dataframes)
        df = df.sort_values([case_id_key, timestamp_key])
    else:
        df = VERSIONS[variant](path, parameters=parameters)

    return df


def import_log(path, parameters=None, variant=DEFAULT_VARIANT_LOG):
    """
    Import a Parquet file

    Parameters
    -------------
    path
        Path of the file to import
    parameters
        Parameters of the algorithm, possible values:
            columns -> columns to import from the Parquet file
    variant
        Variant of the algorithm, possible values: pyarrow

    Returns
    -------------
    df
        Pandas dataframe
    """
    if parameters is None:
        parameters = {}

    return VERSIONS_LOG[variant](path, parameters=parameters)


def import_minimal_log(path, parameters=None, variant=DEFAULT_VARIANT_LOG):
    """
    Import a Parquet file (as a minimal log with only the essential columns)

    Parameters
    -------------
    path
        Path of the file to import
    parameters
        Parameters of the algorithm, possible values:
            columns -> columns to import from the Parquet file
    variant
        Variant of the algorithm, possible values: pyarrow

    Returns
    -------------
    df
        Pandas dataframe
    """
    if parameters is None:
        parameters = {}

    parameters[COLUMNS] = [constants.CASE_CONCEPT_NAME, xes.DEFAULT_NAME_KEY, xes.DEFAULT_TIMESTAMP_KEY]

    return VERSIONS_LOG[variant](path, parameters=parameters)


def import_df(path, parameters=None, variant=DEFAULT_VARIANT):
    """
    Import a Parquet file

    Parameters
    -------------
    path
        Path of the file to import
    parameters
        Parameters of the algorithm, possible values:
            columns -> columns to import from the Parquet file
    variant
        Variant of the algorithm, possible values: pyarrow

    Returns
    -------------
    df
        Pandas dataframe
    """
    return apply(path, variant=variant, parameters=parameters)


def get_list_parquet(path, parameters=None):
    """
    Gets the list of Parquets contained into a dataset

    Parameters
    -------------
    path
        Path where the dataset is
    parameters
        Possible parameters of the algorithm

    Returns
    -------------
    paths
        List of paths
    """
    if parameters is None:
        parameters = {}

    paths = []
    subelements = os.listdir(path)
    for subel in subelements:
        if os.path.isdir(os.path.join(path, subel)):
            sub2 = os.listdir(os.path.join(path, subel))
            for subel2 in sub2:
                if subel2.endswith(".parquet"):
                    if os.path.isfile(os.path.join(path, subel, subel2)):
                        paths.append(os.path.join(path, subel, subel2))
        else:
            if subel.endswith(".parquet"):
                if os.path.isfile(os.path.join(path, subel)):
                    paths.append(os.path.join(path, subel))
    return paths

import os
import pandas as pd

from pm4py.util import constants, exec_utils
from pm4py.util import xes_constants as xes
from enum import Enum

import deprecation
import traceback

VERSIONS = dict()
VERSIONS_LOG = dict()

DEFAULT_VARIANT = None
DEFAULT_VARIANT_LOG = None

Variants = None

try:
    from pm4py.objects.log.importer.parquet.versions import fastparquet

    VERSIONS["fastparquet"] = fastparquet
except:
    # Fastparquet is not installed
    # traceback.print_exc()
    pass

try:
    from pm4py.objects.log.importer.parquet.versions import pyarrow

    VERSIONS["pyarrow"] = pyarrow
    VERSIONS_LOG["pyarrow"] = pyarrow
except:
    # Pyarrow is not installed
    # traceback.print_exc()
    pass


class Parameters(Enum):
    COLUMNS = "columns"


# define the Variants enum dynamically (since when defined cannot be changed)
versions_keys = sorted(list(VERSIONS.keys()))
if versions_keys == ["fastparquet", "pyarrow"]:
    class Variants(Enum):
        FASTPARQUET = VERSIONS["fastparquet"]
        PYARROW = VERSIONS["pyarrow"]


    DEFAULT_VARIANT = Variants.PYARROW
    DEFAULT_VARIANT_LOG = Variants.PYARROW
elif versions_keys == ["pyarrow"]:
    class Variants(Enum):
        PYARROW = VERSIONS["pyarrow"]


    DEFAULT_VARIANT = Variants.PYARROW
    DEFAULT_VARIANT_LOG = Variants.PYARROW
elif versions_keys == ["fastparquet"]:
    class Variants(Enum):
        FASTPARQUET = VERSIONS["fastparquet"]


    DEFAULT_VARIANT = Variants.FASTPARQUET

COLUMNS = Parameters.COLUMNS.value


@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Please import the parquet to a pandas df, then convert it to an event log, if needed')
def apply(path, parameters=None, variant=DEFAULT_VARIANT):
    """
    Import a Parquet file

    Parameters
    -------------
    path
        Path of the file to import
    parameters
        Parameters of the algorithm, possible values:
            Parameters.COLUMNS -> columns to import from the Parquet file
    variant
        Variant of the algorithm, possible values:
            - Variants.PYARROW
            - Variants.FASTPARQUET

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
            dataframes.append(exec_utils.get_variant(variant).apply(file, parameters=parameters))
        df = pd.concat(dataframes)
        df = df.sort_values([case_id_key, timestamp_key])
    else:
        df = exec_utils.get_variant(variant).apply(path, parameters=parameters)

    return df


@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Please import the parquet to a pandas df, then convert it to an event log, if needed')
def import_log(path, parameters=None, variant=DEFAULT_VARIANT_LOG):
    """
    Import a Parquet file

    Parameters
    -------------
    path
        Path of the file to import
    parameters
        Parameters of the algorithm, possible values:
            Parameters.COLUMNS -> columns to import from the Parquet file
    variant
        Variant of the algorithm, possible values:
            - Variants.PYARROW

    Returns
    -------------
    df
        Pandas dataframe
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).import_log(path, parameters=parameters)


@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Please import the parquet to a pandas df, then convert it to an event log, if needed')
def import_minimal_log(path, parameters=None, variant=DEFAULT_VARIANT_LOG):
    """
    Import a Parquet file (as a minimal log with only the essential columns)

    Parameters
    -------------
    path
        Path of the file to import
    parameters
        Parameters of the algorithm, possible values:
            Parameters.COLUMNS -> columns to import from the Parquet file
    variant
        Variant of the algorithm, possible values:
            - Variants.PYARROW

    Returns
    -------------
    df
        Pandas dataframe
    """
    if parameters is None:
        parameters = {}

    parameters[COLUMNS] = [constants.CASE_CONCEPT_NAME, xes.DEFAULT_NAME_KEY, xes.DEFAULT_TIMESTAMP_KEY]

    return exec_utils.get_variant(variant).import_log(path, parameters=parameters)


@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Please import the parquet to a pandas df, then convert it to an event log, if needed')
def import_df(path, parameters=None, variant=DEFAULT_VARIANT):
    """
    Import a Parquet file

    Parameters
    -------------
    path
        Path of the file to import
    parameters
        Parameters of the algorithm, possible values:
            Parameters.COLUMNS -> columns to import from the Parquet file
    variant
        Variant of the algorithm, possible values:
            - Variants.PYARROW

    Returns
    -------------
    df
        Pandas dataframe
    """
    return apply(path, variant=variant, parameters=parameters)


@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='Please import the parquet to a pandas df, then convert it to an event log, if needed')
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

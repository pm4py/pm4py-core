from pm4py.objects.log.importer.parquet.versions import pyarrow
import os
import pandas as pd
from pm4py.util import constants
from pm4py.objects.log.util import xes
from pm4py.algo.filtering.common.filtering_constants import CASE_CONCEPT_NAME

PYARROW = "pyarrow"

VERSIONS = {PYARROW: pyarrow.apply}

COLUMNS = "columns"


def apply(path, parameters=None, variant=PYARROW):
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
        constants.PARAMETER_CONSTANT_CASEID_KEY] if constants.PARAMETER_CONSTANT_CASEID_KEY in parameters else CASE_CONCEPT_NAME

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


def import_log(path, parameters=None, variant=PYARROW):
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


def import_df(path, parameters=None, variant=PYARROW):
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

'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
from enum import Enum
from typing import Optional, Dict, Any, List

import pandas as pd

from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.obj import EventStream
from pm4py.util import constants
from pm4py.util import exec_utils
from pm4py.util import points_subset
from pm4py.util import xes_constants

LEGACY_PARQUET_TP_REPLACER = "AAA"
LEGACY_PARQUET_CASECONCEPTNAME = "caseAAAconceptAAAname"


class Parameters(Enum):
    PARTITION_COLUMN = "partition_column"
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    MANDATORY_ATTRIBUTES = "mandatory_attributes"
    MAX_NO_CASES = "max_no_cases"
    MIN_DIFFERENT_OCC_STR_ATTR = 5
    MAX_DIFFERENT_OCC_STR_ATTR = 50


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

    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
    partition_column = exec_utils.get_param_value(Parameters.PARTITION_COLUMN, parameters, "@@partitioning")

    df[partition_column] = df[case_id_key].rank(method='dense', ascending=False).astype(int) % num_partitions

    return df


def legacy_parquet_support(df, parameters=None):
    """
    For legacy support, Parquet files columns could not contain
    a ":" that has been arbitrarily replaced by a replacer string.
    This string substitutes the replacer to the :

    Parameters
    ---------------
    dataframe
        Dataframe
    parameters
        Parameters of the algorithm
    """
    if parameters is None:
        parameters = {}

    df.columns = [x.replace(LEGACY_PARQUET_TP_REPLACER, ":") for x in df.columns]

    return df


def table_to_stream(table, parameters=None):
    """
    Converts a Pyarrow table to an event stream

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
    # for legacy format support
    if LEGACY_PARQUET_CASECONCEPTNAME in keys:
        for key in keys:
            dict0[key.replace(LEGACY_PARQUET_TP_REPLACER, ":")] = dict0.pop(key)

    stream = EventStream([dict(zip(dict0, i)) for i in zip(*dict0.values())])

    return stream


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

    stream = table_to_stream(table, parameters=parameters)

    return log_converter.apply(stream, parameters=parameters)


def convert_timestamp_columns_in_df(df, timest_format=None, timest_columns=None):
    """
    Convert all dataframe columns in a dataframe

    Parameters
    -----------
    df
        Dataframe
    timest_format
        (If provided) Format of the timestamp columns in the CSV file
    timest_columns
        Columns of the CSV that shall be converted into timestamp

    Returns
    ------------
    df
        Dataframe with timestamp columns converted

    """
    for col in df.columns:
        if timest_columns is None or col in timest_columns:
            if df[col].dtype == 'object':
                try:
                    if timest_format is None:
                        # makes operations faster if non-ISO8601 but anyhow regular dates are provided
                        df[col] = pd.to_datetime(df[col], utc=True, infer_datetime_format=True)
                    else:
                        df[col] = pd.to_datetime(df[col], utc=True, format=timest_format)
                except:
                    # print("exception converting column: "+str(col))
                    pass
    return df


def sample_dataframe(df, parameters=None):
    """
    Sample a dataframe on a given number of cases

    Parameters
    --------------
    df
        Dataframe
    parameters
        Parameters of the algorithm, including:
        - Parameters.CASE_ID_KEY
        - Parameters.CASE_ID_TO_RETAIN

    Returns
    -------------
    sampled_df
        Sampled dataframe
    """
    if parameters is None:
        parameters = {}

    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
    max_no_cases = exec_utils.get_param_value(Parameters.MAX_NO_CASES, parameters, 100)

    case_ids = list(df[case_id_key].unique())
    case_id_to_retain = points_subset.pick_chosen_points_list(min(max_no_cases, len(case_ids)), case_ids)

    return df[df[case_id_key].isin(case_id_to_retain)]


def automatic_feature_selection_df(df, parameters=None):
    """
    Performs an automatic feature selection on dataframes,
    keeping the features useful for ML purposes

    Parameters
    ---------------
    df
        Dataframe
    parameters
        Parameters of the algorithm

    Returns
    ---------------
    featured_df
        Dataframe with only the features that have been selected
    """
    if parameters is None:
        parameters = {}

    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
    mandatory_attributes = exec_utils.get_param_value(Parameters.MANDATORY_ATTRIBUTES, parameters,
                                                      set(df.columns).intersection(
                                                          {constants.CASE_CONCEPT_NAME, xes_constants.DEFAULT_NAME_KEY,
                                                           xes_constants.DEFAULT_TIMESTAMP_KEY}))

    min_different_occ_str_attr = exec_utils.get_param_value(Parameters.MIN_DIFFERENT_OCC_STR_ATTR, parameters, 5)
    max_different_occ_str_attr = exec_utils.get_param_value(Parameters.MAX_DIFFERENT_OCC_STR_ATTR, parameters, 50)

    cols_dtypes = {x: str(df[x].dtype) for x in df.columns}
    other_attributes_to_retain = set()

    no_all_cases = df[case_id_key].nunique()
    for x, y in cols_dtypes.items():
        attr_df = df.dropna(subset=[x])
        this_cases = attr_df[case_id_key].nunique()

        # in any case, keep attributes that appears at least once per case
        if this_cases == no_all_cases:
            if "float" in y or "int" in y:
                # (as in the classic log version) retain always float/int attributes
                other_attributes_to_retain.add(x)
            elif "object" in y:
                # (as in the classic log version) keep string attributes if they have enough variability, but not too much
                # (that would be hard to explain)
                unique_val_count = df[x].nunique()
                if min_different_occ_str_attr <= unique_val_count <= max_different_occ_str_attr:
                    other_attributes_to_retain.add(x)
            else:
                # not consider the attribute after this feature selection if it has other types (for example, date)
                pass

    attributes_to_retain = mandatory_attributes.union(other_attributes_to_retain)

    return df[attributes_to_retain]


def select_number_column(df: pd.DataFrame, fea_df: pd.DataFrame, col: str,
                         case_id_key=constants.CASE_CONCEPT_NAME) -> pd.DataFrame:
    """
    Extract a column for the features dataframe for the given numeric attribute

    Parameters
    --------------
    df
        Dataframe
    fea_df
        Feature dataframe
    col
        Numeric column
    case_id_key
        Case ID key

    Returns
    --------------
    fea_df
        Feature dataframe (desidered output)
    """
    df = df.dropna(subset=[col]).groupby(case_id_key).last().reset_index()[[case_id_key, col]]
    fea_df = fea_df.merge(df, on=[case_id_key], how="left", suffixes=('', '_y'))
    return fea_df


def select_string_column(df: pd.DataFrame, fea_df: pd.DataFrame, col: str,
                         case_id_key=constants.CASE_CONCEPT_NAME) -> pd.DataFrame:
    """
    Extract N columns (for N different attribute values; hotencoding) for the features dataframe for the given string attribute

    Parameters
    --------------
    df
        Dataframe
    fea_df
        Feature dataframe
    col
        String column
    case_id_key
        Case ID key

    Returns
    --------------
    fea_df
        Feature dataframe (desidered output)
    """
    vals = df[col].unique()
    for val in vals:
        if val is not None:
            filt_df_cases = df[df[col] == val][case_id_key].unique()
            new_col = col + "_" + val.encode('ascii', errors='ignore').decode('ascii').replace(" ", "")
            fea_df[new_col] = fea_df[case_id_key].isin(filt_df_cases)
            fea_df[new_col] = fea_df[new_col].astype("int")
    return fea_df


def get_features_df(df: pd.DataFrame, list_columns: List[str],
                    parameters: Optional[Dict[Any, Any]] = None) -> pd.DataFrame:
    """
    Given a dataframe and a list of columns, performs an automatic feature extraction

    Parameters
    ---------------
    df
        Dataframe
    list_column
        List of column to consider in the feature extraction
    parameters
        Parameters of the algorithm, including:
        - Parameters.CASE_ID_KEY: the case ID

    Returns
    ---------------
    fea_df
        Feature dataframe (desidered output)
    """
    if parameters is None:
        parameters = {}

    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)

    fea_df = pd.DataFrame({case_id_key: sorted(list(df[case_id_key].unique()))})
    for col in list_columns:
        if "object" in str(df[col].dtype):
            fea_df = select_string_column(df, fea_df, col, case_id_key=case_id_key)
        elif "float" in str(df[col].dtype) or "int" in str(df[col].dtype):
            fea_df = select_number_column(df, fea_df, col, case_id_key=case_id_key)
    fea_df = fea_df.sort_values(case_id_key)
    return fea_df


def automatic_feature_extraction_df(df: pd.DataFrame, parameters: Optional[Dict[Any, Any]] = None) -> pd.DataFrame:
    """
    Performs an automatic feature extraction given a dataframe

    Parameters
    --------------
    df
        Dataframe
    parameters
        Parameters of the algorithm, including:
        - Parameters.CASE_ID_KEY: the case ID
        - Parameters.MIN_DIFFERENT_OCC_STR_ATTR
        - Parameters.MAX_DIFFERENT_OCC_STR_ATTR

    Returns
    --------------
    fea_df
        Dataframe with the features
    """
    if parameters is None:
        parameters = {}

    fea_sel_df = automatic_feature_selection_df(df, parameters=parameters)
    columns = set(fea_sel_df.columns)
    columns.remove(constants.CASE_CONCEPT_NAME)
    columns.remove(xes_constants.DEFAULT_TIMESTAMP_KEY)

    return get_features_df(fea_sel_df, columns, parameters=parameters)

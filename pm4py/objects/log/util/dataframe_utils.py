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
from pm4py.util import xes_constants, pandas_utils
from pm4py.util.dt_parsing.variants import strpfromiso
import numpy as np
import random
import traceback


LEGACY_PARQUET_TP_REPLACER = "AAA"
LEGACY_PARQUET_CASECONCEPTNAME = "caseAAAconceptAAAname"


class Parameters(Enum):
    PARTITION_COLUMN = "partition_column"
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    CASE_PREFIX = constants.CASE_ATTRIBUTE_PREFIX
    CASE_ATTRIBUTES = "case_attributes"
    MANDATORY_ATTRIBUTES = "mandatory_attributes"
    MAX_NO_CASES = "max_no_cases"
    MIN_DIFFERENT_OCC_STR_ATTR = 5
    MAX_DIFFERENT_OCC_STR_ATTR = 50
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    PARAM_ARTIFICIAL_START_ACTIVITY = constants.PARAM_ARTIFICIAL_START_ACTIVITY
    PARAM_ARTIFICIAL_END_ACTIVITY = constants.PARAM_ARTIFICIAL_END_ACTIVITY
    INDEX_KEY = "index_key"
    CASE_INDEX_KEY = "case_index_key"
    USE_EXTREMES_TIMESTAMP = "use_extremes_timestamp"
    ADD_CASE_IDENTIFIER_COLUMN = "add_case_identifier_column"
    DETERMINISTIC = "deterministic"


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

    case_index_key = exec_utils.get_param_value(Parameters.CASE_INDEX_KEY, parameters, constants.DEFAULT_CASE_INDEX_KEY)
    partition_column = exec_utils.get_param_value(Parameters.PARTITION_COLUMN, parameters, "@@partitioning")

    if case_index_key not in df.columns:
        from pm4py.util import pandas_utils
        df = pandas_utils.insert_case_index(df, case_index_key)

    df[partition_column] = df[case_index_key] % num_partitions

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
    if timest_format is None:
        timest_format = constants.DEFAULT_TIMESTAMP_PARSE_FORMAT

    if timest_format is None:
        timest_format = "mixed"

    for col in df.columns:
        if timest_columns is None or col in timest_columns:
            if "obj" in str(df[col].dtype) or "str" in str(df[col].dtype):
                try:
                    df[col] = pandas_utils.dataframe_column_string_to_datetime(df[col], format=timest_format, utc=True)
                except:
                    try:
                        df[col] = pandas_utils.dataframe_column_string_to_datetime(df[col], format=timest_format, exact=False, utc=True)
                    except:
                        try:
                            df[col] = pandas_utils.dataframe_column_string_to_datetime(df[col], format=timest_format)
                        except:
                            pass

    for col in df.columns:
        if "date" in str(df[col].dtype) or "time" in str(df[col].dtype):
            df[col] = strpfromiso.fix_dataframe_column(df[col])

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

    deterministic = exec_utils.get_param_value(Parameters.DETERMINISTIC, parameters, False)
    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
    max_no_cases = exec_utils.get_param_value(Parameters.MAX_NO_CASES, parameters, 100)

    case_ids = pandas_utils.format_unique(df[case_id_key].unique())
    case_ids = list(case_ids)

    if not deterministic:
        random.shuffle(case_ids)

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
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)

    mandatory_attributes = exec_utils.get_param_value(Parameters.MANDATORY_ATTRIBUTES, parameters,
                                                      set(df.columns).intersection(
                                                          {case_id_key, activity_key,
                                                           timestamp_key}))

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
            elif "obj" in y or "str" in y:
                # (as in the classic log version) keep string attributes if they have enough variability, but not too much
                # (that would be hard to explain)
                unique_val_count = df[x].nunique()
                if min_different_occ_str_attr <= unique_val_count <= max_different_occ_str_attr:
                    other_attributes_to_retain.add(x)
            else:
                # not consider the attribute after this feature selection if it has other types (for example, date)
                pass

    attributes_to_retain = mandatory_attributes.union(other_attributes_to_retain)

    return df[list(attributes_to_retain)]


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
    fea_df[col] = fea_df[col].astype(np.float32)
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
    vals = pandas_utils.format_unique(df[col].unique())
    for val in vals:
        if val is not None:
            filt_df_cases = pandas_utils.format_unique(df[df[col] == val][case_id_key].unique())
            new_col = col + "_" + val.encode('ascii', errors='ignore').decode('ascii').replace(" ", "")
            fea_df[new_col] = fea_df[case_id_key].isin(filt_df_cases)
            fea_df[new_col] = fea_df[new_col].astype(np.float32)
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
    add_case_identifier_column = exec_utils.get_param_value(Parameters.ADD_CASE_IDENTIFIER_COLUMN, parameters, False)

    fea_df = pandas_utils.instantiate_dataframe({case_id_key: sorted(pandas_utils.format_unique(df[case_id_key].unique()))})
    for col in list_columns:
        if "obj" in str(df[col].dtype) or "str" in str(df[col].dtype):
            fea_df = select_string_column(df, fea_df, col, case_id_key=case_id_key)
        elif "float" in str(df[col].dtype) or "int" in str(df[col].dtype):
            fea_df = select_number_column(df, fea_df, col, case_id_key=case_id_key)
    fea_df = fea_df.sort_values(case_id_key)
    if not add_case_identifier_column:
        del fea_df[case_id_key]

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

    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)

    fea_sel_df = automatic_feature_selection_df(df, parameters=parameters)
    columns = set(fea_sel_df.columns)

    if case_id_key in columns:
        columns.remove(case_id_key)

    if timestamp_key in columns:
        columns.remove(timestamp_key)

    return get_features_df(fea_sel_df, list(columns), parameters=parameters)


def insert_artificial_start_end(df0: pd.DataFrame, parameters: Optional[Dict[Any, Any]] = None) -> pd.DataFrame:
    """
    Inserts the artificial start/end activities in a Pandas dataframe

    Parameters
    ------------------
    df0
        Dataframe
    parameters
        Parameters of the algorithm, including:
        - Parameters.CASE_ID_KEY: the case identifier
        - Parameters.TIMESTAMP_KEY: the timestamp
        - Parameters.ACTIVITY_KEY: the activity

    Returns
    -----------------
    enriched_df
        Dataframe with artificial start/end activities
    """
    if parameters is None:
        parameters = {}

    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    use_extremes_timestamp = exec_utils.get_param_value(Parameters.USE_EXTREMES_TIMESTAMP, parameters, False)

    artificial_start_activity = exec_utils.get_param_value(Parameters.PARAM_ARTIFICIAL_START_ACTIVITY, parameters, constants.DEFAULT_ARTIFICIAL_START_ACTIVITY)
    artificial_end_activity = exec_utils.get_param_value(Parameters.PARAM_ARTIFICIAL_END_ACTIVITY, parameters, constants.DEFAULT_ARTIFICIAL_END_ACTIVITY)

    index_key = exec_utils.get_param_value(Parameters.INDEX_KEY, parameters, constants.DEFAULT_INDEX_KEY)

    df = df0.copy()
    df = pandas_utils.insert_index(df, index_key)
    df = df.sort_values([case_id_key, timestamp_key, index_key])

    start_df = df[[case_id_key, timestamp_key]].groupby(case_id_key).first().reset_index()
    end_df = df[[case_id_key, timestamp_key]].groupby(case_id_key).last().reset_index()
    # stability trick: remove 1ms from the artificial start activity timestamp, add 1ms to the artificial end activity timestamp
    if use_extremes_timestamp:
        start_df[timestamp_key] = pd.Timestamp.min
        end_df[timestamp_key] = pd.Timestamp.max
        start_df[timestamp_key] = start_df[timestamp_key].dt.tz_localize("utc")
        end_df[timestamp_key] = end_df[timestamp_key].dt.tz_localize("utc")
    else:
        start_df[timestamp_key] = start_df[timestamp_key] - pd.Timedelta("1 ms")
        end_df[timestamp_key] = end_df[timestamp_key] + pd.Timedelta("1 ms")

    start_df[activity_key] = artificial_start_activity
    end_df[activity_key] = artificial_end_activity

    df = pandas_utils.concat([start_df, df, end_df])
    df = pandas_utils.insert_index(df, index_key)
    df = df.sort_values([case_id_key, timestamp_key, index_key])

    df.attrs = df0.attrs

    return df


def dataframe_to_activity_case_table(df: pd.DataFrame, parameters: Optional[Dict[Any, Any]] = None):
    """
    Transforms a Pandas dataframe into:
    - an "activity" table, containing the events and their attributes
    - a "case" table, containing the cases and their attributes

    Parameters
    --------------
    df
        Dataframe
    parameters
        Parameters of the algorithm that should be used, including:
        - Parameters.CASE_ID_KEY => the column to be used as case ID (shall be included both in the activity table and the case table)
        - Parameters.CASE_PREFIX => if a list of attributes at the case level is not provided, then all the ones of the dataframe
                                    starting with one of these are considered.
        - Parameters.CASE_ATTRIBUTES => the attributes of the dataframe to be used as case columns

    Returns
    ---------------
    activity_table
        Activity table
    case_table
        Case table
    """
    if parameters is None:
        parameters = {}

    # make sure we start from a dataframe object
    df = log_converter.apply(df, variant=log_converter.Variants.TO_DATA_FRAME, parameters=parameters)

    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
    case_id_prefix = exec_utils.get_param_value(Parameters.CASE_PREFIX, parameters, constants.CASE_ATTRIBUTE_PREFIX)

    case_attributes = exec_utils.get_param_value(Parameters.CASE_ATTRIBUTES, parameters, set([x for x in df.columns if x.startswith(case_id_prefix)]))
    event_attributes = set([x for x in df.columns if x not in case_attributes])

    activity_table = df[event_attributes.union({case_id_key})]
    case_table = df[case_attributes.union({case_id_key})].groupby(case_id_key).first().reset_index()

    return activity_table, case_table

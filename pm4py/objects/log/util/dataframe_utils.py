from pm4py.util import constants
from pm4py.objects.log.log import EventStream
from pm4py.objects.conversion.log import converter as log_converter
import pandas as pd
from pm4py.util.versions import check_pandas_ge_024
from enum import Enum
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
    needs_conversion = check_pandas_ge_024()
    for col in df.columns:
        if timest_columns is None or col in timest_columns:
            if df[col].dtype == 'object':
                try:
                    if timest_format is None:
                        if needs_conversion:
                            df[col] = pd.to_datetime(df[col], utc=True)
                        else:
                            df[col] = pd.to_datetime(df[col])
                    else:
                        if needs_conversion:
                            df[col] = pd.to_datetime(df[col], utc=True, format=timest_format)
                        else:
                            df[col] = pd.to_datetime(df[col])
                except ValueError:
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

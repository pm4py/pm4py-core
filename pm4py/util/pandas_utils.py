import pkgutil

import pandas as pd

from pm4py.util import constants, xes_constants
import deprecation


def to_dict_records(df):
    """
    Pandas dataframe to dictionary (records method)

    Parameters
    ---------------
    df
        Dataframe

    Returns
    --------------
    list_dictio
        List containing a dictionary for each row
    """
    return df.to_dict('records')


def to_dict_index(df):
    """
    Pandas dataframe to dictionary (index method)

    Parameters
    ---------------
    df
        Dataframe

    Returns
    --------------
    dict
        dict like {index -> {column -> value}}
    """
    return df.to_dict('index')


def insert_index(df, column_name=constants.DEFAULT_INDEX_KEY):
    """
    Inserts the dataframe index in the specified column

    Parameters
    --------------
    df
        Dataframe
    column_name
        Name of the column that should host the index

    Returns
    --------------
    df
        Dataframe with index
    """
    df = df.copy()
    df[column_name] = df.index
    return df


def insert_ev_in_tr_index(df: pd.DataFrame, case_id: str = constants.CASE_CONCEPT_NAME,
                          column_name: str = constants.DEFAULT_INDEX_IN_TRACE_KEY) -> pd.DataFrame:
    """
    Inserts a column that specify the index of the event inside the case

    Parameters
    ---------------
    df
        Dataframe
    case_id
        Column that hosts the case identifier
    column_name
        Name of the column that should host the index

    Returns
    --------------
    df
        Dataframe with index
    """
    df = df.copy()
    df_trace_idx = df.groupby(case_id).cumcount()
    df[column_name] = df_trace_idx
    return df


@deprecation.deprecated('2.2.8', '3.0.0', details="use check_is_pandas_dataframe instead")
def check_is_dataframe(log):
    """
    Checks if a log object is a dataframe

    Parameters
    -------------
    log
        Log object

    Returns
    -------------
    boolean
        Is dataframe?
    """
    if pkgutil.find_loader("pandas"):
        import pandas as pd
        return type(log) is pd.DataFrame
    return False


@deprecation.deprecated('2.2.8', '3.0.0', details="use check_pandas_dataframe_columns instead")
def check_dataframe_columns(df):
    """
    Checks if the dataframe contains all the required columns.
    If not, raise an exception

    Parameters
    --------------
    df
        Pandas dataframe
    """
    if len(set(df.columns).intersection(
            set([constants.CASE_CONCEPT_NAME, xes_constants.DEFAULT_NAME_KEY,
                 xes_constants.DEFAULT_TIMESTAMP_KEY]))) < 3:
        raise Exception(
            "please format your dataframe accordingly! df = pm4py.format_dataframe(df, case_id='<name of the case ID column>', activity_key='<name of the activity column>', timestamp_key='<name of the timestamp column>')")



def check_is_pandas_dataframe(log):
    """
    Checks if a log object is a dataframe

    Parameters
    -------------
    log
        Log object

    Returns
    -------------
    boolean
        Is dataframe?
    """
    if pkgutil.find_loader("pandas"):
        import pandas as pd
        return type(log) is pd.DataFrame
    return False


def check_pandas_dataframe_columns(df):
    """
    Checks if the dataframe contains all the required columns.
    If not, raise an exception

    Parameters
    --------------
    df
        Pandas dataframe
    """
    if len(set(df.columns).intersection(
            set([constants.CASE_CONCEPT_NAME, xes_constants.DEFAULT_NAME_KEY,
                 xes_constants.DEFAULT_TIMESTAMP_KEY]))) < 3:
        raise Exception(
            "please format your dataframe accordingly! df = pm4py.format_dataframe(df, case_id='<name of the case ID column>', activity_key='<name of the activity column>', timestamp_key='<name of the timestamp column>')")

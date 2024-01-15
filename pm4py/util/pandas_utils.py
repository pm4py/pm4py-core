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
import pandas as pd
import importlib.util

from pm4py.util import constants, xes_constants
import numpy as np


def get_default_dataframe_environment():
    if importlib.util.find_spec("cudf"):
        #import cudf; return cudf
        import cudf.pandas
        cudf.pandas.install()
    import pandas as pd
    return pd


DATAFRAME = get_default_dataframe_environment()


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


def insert_index(df, column_name=constants.DEFAULT_INDEX_KEY, copy_dataframe=True, reset_index=True):
    """
    Inserts the dataframe index in the specified column

    Parameters
    --------------
    df
        Dataframe
    column_name
        Name of the column that should host the index
    copy_dataframe
        Establishes if the original dataframe should be copied before inserting the column

    Returns
    --------------
    df
        Dataframe with index
    """
    if copy_dataframe:
        df = df.copy()

    if reset_index:
        df = df.reset_index(drop=True)

    df[column_name] = df.index
    return df


def insert_case_index(df, column_name=constants.DEFAULT_CASE_INDEX_KEY, case_id=constants.CASE_CONCEPT_NAME, copy_dataframe=True):
    """
    Inserts the case number in the dataframe

    Parameters
    ---------------
    df
        Dataframe
    column_name
        Name of the column that should host the case index
    case_id
        Case identifier
    copy_dataframe
        Establishes if the original dataframe should be copied before inserting the column

    Returns
    ---------------
    df
        Dataframe with case index
    """
    if copy_dataframe:
        df = df.copy()

    df[column_name] = df.groupby(case_id).ngroup()
    return df


def insert_ev_in_tr_index(df: pd.DataFrame, case_id: str = constants.CASE_CONCEPT_NAME,
                          column_name: str = constants.DEFAULT_INDEX_IN_TRACE_KEY, copy_dataframe=True) -> pd.DataFrame:
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
    if copy_dataframe:
        df = df.copy()

    df_trace_idx = df.groupby(case_id).cumcount()
    df[column_name] = df_trace_idx
    return df


def format_unique(values):
    try:
        values = values.to_numpy()
    except:
        pass

    values = values.tolist()
    return values


def insert_feature_activity_position_in_trace(df: pd.DataFrame, case_id: str = constants.CASE_CONCEPT_NAME,
                                      activity_key: str = xes_constants.DEFAULT_NAME_KEY, prefix="@@position_"):
    """
    Inserts additional columns @@position_ACT1, @@position_ACT2 ...
    which are populated for every event having activity ACT1, ACT2 respectively,
    with the index of the event inside its case.

    Parameters
    ------------------
    df
        Pandas dataframe
    case_id
        Case idntifier
    activity_key
        Activity
    prefix
        Prefix of the "activity position in trace" feature (default: @@position_)

    Returns
    ------------------
    df
        Pandas dataframe
    """
    df = insert_ev_in_tr_index(df, case_id=case_id)
    activities = format_unique(df[activity_key].unique())
    for act in activities:
        df[prefix + act] = df[activity_key].apply(lambda x: np.nan if x == act else -1)
        df[prefix + act] = df[prefix + act].fillna(df[constants.DEFAULT_INDEX_IN_TRACE_KEY])
        df[prefix + act] = df[prefix + act].replace(-1, np.nan)
    return df


def insert_case_arrival_finish_rate(log: pd.DataFrame, case_id_column=constants.CASE_CONCEPT_NAME, timestamp_column=xes_constants.DEFAULT_TIMESTAMP_KEY, start_timestamp_column=None, arrival_rate_column="@@arrival_rate", finish_rate_column="@@finish_rate") -> pd.DataFrame:
    """
    Inserts the arrival/finish rate in the dataframe.

    Parameters
    -----------------
    log
        Pandas dataframe

    Returns
    -----------------
    log
        Pandas dataframe enriched by arrival and finish rate
    """
    if start_timestamp_column is None:
        start_timestamp_column = timestamp_column

    case_arrival = log.groupby(case_id_column)[start_timestamp_column].agg("min").to_dict()
    case_arrival = [[x, y.timestamp()] for x, y in case_arrival.items()]
    case_arrival.sort(key=lambda x: (x[1], x[0]))

    case_finish = log.groupby(case_id_column)[timestamp_column].agg("max").to_dict()
    case_finish = [[x, y.timestamp()] for x, y in case_finish.items()]
    case_finish.sort(key=lambda x: (x[1], x[0]))

    i = len(case_arrival) - 1
    while i > 0:
        case_arrival[i][1] = case_arrival[i][1] - case_arrival[i-1][1]
        i = i - 1
    case_arrival[0][1] = 0
    case_arrival = {x[0]: x[1] for x in case_arrival}

    i = len(case_finish) - 1
    while i > 0:
        case_finish[i][1] = case_finish[i][1] - case_finish[i-1][1]
        i = i - 1
    case_finish[0][1] = 0
    case_finish = {x[0]: x[1] for x in case_finish}

    log[arrival_rate_column] = log[case_id_column].map(case_arrival)
    log[finish_rate_column] = log[case_id_column].map(case_finish)

    return log


def insert_case_service_waiting_time(log: pd.DataFrame, case_id_column=constants.CASE_CONCEPT_NAME, timestamp_column=xes_constants.DEFAULT_TIMESTAMP_KEY, start_timestamp_column=None, diff_start_end_column="@@diff_start_end", service_time_column="@@service_time", sojourn_time_column="@@sojourn_time", waiting_time_column="@@waiting_time") -> pd.DataFrame:
    """
    Inserts the service/waiting/sojourn time in the dataframe.

    Parameters
    ----------------
    log
        Pandas dataframe
    parameters
        Parameters of the method

    Returns
    ----------------
    log
        Pandas dataframe with service, waiting and sojourn time
    """
    if start_timestamp_column is None:
        start_timestamp_column = timestamp_column

    log[diff_start_end_column] = get_total_seconds(log[timestamp_column] - log[start_timestamp_column])
    service_times = log.groupby(case_id_column)[diff_start_end_column].sum().to_dict()
    log[service_time_column] = log[case_id_column].map(service_times)

    start_timestamps = log.groupby(case_id_column)[start_timestamp_column].agg("min").to_dict()
    complete_timestamps = log.groupby(case_id_column)[timestamp_column].agg("max").to_dict()
    sojourn_time_cases = {x: complete_timestamps[x].timestamp() - start_timestamps[x].timestamp() for x in start_timestamps}

    log[sojourn_time_column] = log[case_id_column].map(sojourn_time_cases)
    log[waiting_time_column] = log[sojourn_time_column] - log[service_time_column]

    return log


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
    log_type = str(type(log)).lower()
    return "dataframe" in log_type


def instantiate_dataframe(*args, **kwargs):
    return DATAFRAME.DataFrame(*args, **kwargs)


def instantiate_dataframe_from_dict(*args, **kwargs):
    return DATAFRAME.DataFrame.from_dict(*args, **kwargs)


def instantiate_dataframe_from_records(*args, **kwargs):
    return DATAFRAME.DataFrame.from_records(*args, **kwargs)


def get_grouper(*args, **kwargs):
    return DATAFRAME.Grouper(*args, **kwargs)


def get_total_seconds(difference):
    return 86400 * difference.dt.days + difference.dt.seconds + 10**-6 * difference.dt.microseconds + 10**-9 * difference.dt.nanoseconds


def convert_to_seconds(dt_column):
    try:
        # Pandas
        return dt_column.values.astype(np.int64) / 10**9
    except:
        # CUDF
        return [x/10**9 for x in dt_column.to_numpy().tolist()]


def dataframe_column_string_to_datetime(*args, **kwargs):
    if importlib.util.find_spec("cudf") or constants.TEST_CUDF_DATAFRAMES_ENVIRONMENT:
        pass
        """if DATAFRAME == pd:
            format = kwargs["format"] if "format" in kwargs else None
            if format not in [None, 'mixed', 'ISO8601']:
                kwargs["exact"] = False"""

    return DATAFRAME.to_datetime(*args, **kwargs)


def read_csv(*args, **kwargs):
    if importlib.util.find_spec("cudf") or constants.TEST_CUDF_DATAFRAMES_ENVIRONMENT:
        if kwargs and "encoding" in kwargs:
            del kwargs["encoding"]

    return DATAFRAME.read_csv(*args, **kwargs)


def concat(*args, **kwargs):
    return DATAFRAME.concat(*args, **kwargs)


def merge(*args, **kwargs):
    return DATAFRAME.merge(*args, **kwargs)


def check_pandas_dataframe_columns(df, activity_key=None, case_id_key=None, timestamp_key=None, start_timestamp_key=None):
    """
    Checks if the dataframe contains all the required columns.
    If not, raise an exception

    Parameters
    --------------
    df
        Pandas dataframe
    """
    if len(df.columns) < 3:
        raise Exception("the dataframe should (at least) contain a column for the case identifier, a column for the activity and a column for the timestamp.")

    str_columns = {x for x in df.columns if "str" in str(df[x].dtype).lower() or "obj" in str(df[x].dtype).lower()}
    timest_columns = {x for x in df.columns if "date" in str(df[x].dtype).lower() or "time" in str(df[x].dtype).lower()}

    if len(str_columns) < 2:
        raise Exception("the dataframe should (at least) contain a column of type string for the case identifier and a column of type string for the activity.")

    if len(timest_columns) < 1:
        raise Exception("the dataframe should (at least) contain a column of type date")

    if case_id_key is not None:
        if case_id_key not in df.columns:
            raise Exception("the specified case ID column is not contained in the dataframe. Available columns: "+str(sorted(list(df.columns))))

        if case_id_key not in str_columns:
            raise Exception("the case ID column should be of type string.")

        if df[case_id_key].isnull().values.any():
            raise Exception("the case ID column should not contain any empty value.")

    if activity_key is not None:
        if activity_key not in df.columns:
            raise Exception("the specified activity column is not contained in the dataframe. Available columns: "+str(sorted(list(df.columns))))

        if activity_key not in str_columns:
            raise Exception("the activity column should be of type string.")

        if df[activity_key].isnull().values.any():
            raise Exception("the activity column should not contain any empty value.")

    if timestamp_key is not None:
        if timestamp_key not in df.columns:
            raise Exception("the specified timestamp column is not contained in the dataframe. Available columns: "+str(sorted(list(df.columns))))

        if timestamp_key not in timest_columns:
            raise Exception("the timestamp column should be of time datetime. Use the function pandas.to_datetime")

        if df[timestamp_key].isnull().values.any():
            raise Exception("the timestamp column should not contain any empty value.")

    if start_timestamp_key is not None:
        if start_timestamp_key not in df.columns:
            raise Exception("the specified start timestamp column is not contained in the dataframe. Available columns: "+str(sorted(list(df.columns))))

        if start_timestamp_key not in timest_columns:
            raise Exception("the start timestamp column should be of time datetime. Use the function pandas.to_datetime")

        if df[start_timestamp_key].isnull().values.any():
            raise Exception("the start timestamp column should not contain any empty value.")

    """if len(set(df.columns).intersection(
            set([constants.CASE_CONCEPT_NAME, xes_constants.DEFAULT_NAME_KEY,
                 xes_constants.DEFAULT_TIMESTAMP_KEY]))) < 3:
        raise Exception(
            "please format your dataframe accordingly! df = pm4py.format_dataframe(df, case_id='<name of the case ID column>', activity_key='<name of the activity column>', timestamp_key='<name of the timestamp column>')")"""

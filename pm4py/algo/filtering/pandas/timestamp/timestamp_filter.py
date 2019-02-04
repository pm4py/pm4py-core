import pandas as pd
import pytz

from pm4py.algo.filtering.common.filtering_constants import CASE_CONCEPT_NAME
from pm4py.algo.filtering.common.timestamp.timestamp_common import get_dt_from_string
from pm4py.objects.log.util.xes import DEFAULT_TIMESTAMP_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_TIMESTAMP_KEY, PARAMETER_CONSTANT_CASEID_KEY
from pm4py.util.versions import check_pandas_ge_024


def filter_traces_contained(df, dt1, dt2, parameters=None):
    """
    Get traces that are contained in the given interval

    Parameters
    ----------
    df
        Pandas dataframe
    dt1
        Lower bound to the interval (possibly expressed as string, but automatically converted)
    dt2
        Upper bound to the interval (possibly expressed as string, but automatically converted)
    parameters
        Possible parameters of the algorithm, including:
            timestamp_key -> Attribute to use as timestamp
            case_id_glue -> Column that contains the timestamp

    Returns
    ----------
    df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}
    timestamp_key = parameters[
        PARAMETER_CONSTANT_TIMESTAMP_KEY] if PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else DEFAULT_TIMESTAMP_KEY
    case_id_glue = parameters[
        PARAMETER_CONSTANT_CASEID_KEY] if PARAMETER_CONSTANT_CASEID_KEY in parameters else CASE_CONCEPT_NAME
    dt1 = get_dt_from_string(dt1)
    dt2 = get_dt_from_string(dt2)
    needs_conversion = check_pandas_ge_024()
    if needs_conversion:
        dt1 = dt1.replace(tzinfo=pytz.utc)
        dt2 = dt2.replace(tzinfo=pytz.utc)
        dt1 = pd.to_datetime(dt1, utc=True)
        dt2 = pd.to_datetime(dt2, utc=True)
    grouped_df = df[[case_id_glue, timestamp_key]].groupby(df[case_id_glue])
    first = grouped_df.first()
    last = grouped_df.last()
    last.columns = [str(col) + '_2' for col in last.columns]
    stacked = pd.concat([first, last], axis=1)
    stacked = stacked[stacked[timestamp_key] > dt1]
    stacked = stacked[stacked[timestamp_key + "_2"] < dt2]
    i1 = df.set_index(case_id_glue).index
    i2 = stacked.set_index(case_id_glue).index
    return df[i1.isin(i2)]


def filter_traces_intersecting(df, dt1, dt2, parameters=None):
    """
    Filter traces intersecting the given interval

    Parameters
    ----------
    df
        Pandas dataframe
    dt1
        Lower bound to the interval (possibly expressed as string, but automatically converted)
    dt2
        Upper bound to the interval (possibly expressed as string, but automatically converted)
    parameters
        Possible parameters of the algorithm, including:
            timestamp_key -> Attribute to use as timestamp
            case_id_glue -> Column that contains the timestamp

    Returns
    ----------
    df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}
    timestamp_key = parameters[
        PARAMETER_CONSTANT_TIMESTAMP_KEY] if PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else DEFAULT_TIMESTAMP_KEY
    case_id_glue = parameters[
        PARAMETER_CONSTANT_CASEID_KEY] if PARAMETER_CONSTANT_CASEID_KEY in parameters else CASE_CONCEPT_NAME
    dt1 = get_dt_from_string(dt1)
    dt2 = get_dt_from_string(dt2)
    needs_conversion = check_pandas_ge_024()
    if needs_conversion:
        dt1 = dt1.replace(tzinfo=pytz.utc)
        dt2 = dt2.replace(tzinfo=pytz.utc)
        dt1 = pd.to_datetime(dt1, utc=True)
        dt2 = pd.to_datetime(dt2, utc=True)
    grouped_df = df[[case_id_glue, timestamp_key]].groupby(df[case_id_glue])
    first = grouped_df.first()
    last = grouped_df.last()
    last.columns = [str(col) + '_2' for col in last.columns]
    stacked = pd.concat([first, last], axis=1)
    stacked1 = stacked[stacked[timestamp_key] > dt1]
    stacked1 = stacked1[stacked1[timestamp_key] < dt2]
    stacked2 = stacked[stacked[timestamp_key + "_2"] > dt1]
    stacked2 = stacked2[stacked2[timestamp_key + "_2"] < dt2]
    stacked3 = stacked[stacked[timestamp_key] < dt1]
    stacked3 = stacked3[stacked3[timestamp_key + "_2"] > dt2]
    stacked = pd.concat([stacked1, stacked2, stacked3], axis=0)
    i1 = df.set_index(case_id_glue).index
    i2 = stacked.set_index(case_id_glue).index
    return df[i1.isin(i2)]


def apply_events(df, dt1, dt2, parameters=None):
    """
    Get a new log containing all the events contained in the given interval

    Parameters
    ----------
    df
        Pandas dataframe
    dt1
        Lower bound to the interval (possibly expressed as string, but automatically converted)
    dt2
        Upper bound to the interval (possibly expressed as string, but automatically converted)
    parameters
        Possible parameters of the algorithm, including:
            timestamp_key -> Attribute to use as timestamp

    Returns
    ----------
    df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}

    timestamp_key = parameters[
        PARAMETER_CONSTANT_TIMESTAMP_KEY] if PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else DEFAULT_TIMESTAMP_KEY
    dt1 = get_dt_from_string(dt1)
    dt2 = get_dt_from_string(dt2)
    needs_conversion = check_pandas_ge_024()
    if needs_conversion:
        dt1 = dt1.replace(tzinfo=pytz.utc)
        dt2 = dt2.replace(tzinfo=pytz.utc)
        dt1 = pd.to_datetime(dt1, utc=True)
        dt2 = pd.to_datetime(dt2, utc=True)

    df = df[df[timestamp_key] > dt1]
    df = df[df[timestamp_key] < dt2]

    return df


def apply(df, parameters=None):
    del df
    del parameters
    raise Exception("apply method not available for timestamp filter")


def apply_auto_filter(df, parameters=None):
    del df
    del parameters
    raise Exception("apply_auto_filter method not available for timestamp filter")

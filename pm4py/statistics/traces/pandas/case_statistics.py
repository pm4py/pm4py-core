import pandas as pd

from pm4py.algo.filtering.common.filtering_constants import CASE_CONCEPT_NAME
from pm4py.objects.log.util import xes
from pm4py.objects.log.util.xes import DEFAULT_TIMESTAMP_KEY
from pm4py.statistics.traces.common import case_duration as case_duration_commons
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_CASEID_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_TIMESTAMP_KEY


def get_variant_statistics(df, parameters=None):
    """
    Get variants from a Pandas dataframe

    Parameters
    -----------
    df
        Dataframe
    parameters
        Parameters of the algorithm, including:
            case_id_glue -> Column that contains the Case ID
            activity_key -> Column that contains the activity
            max_variants_to_return -> Maximum number of variants to return
            variants_df -> If provided, avoid recalculation of the variants dataframe

    Returns
    -----------
    variants_list
        List of variants inside the Pandas dataframe
    """
    if parameters is None:
        parameters = {}
    case_id_glue = parameters[
        PARAMETER_CONSTANT_CASEID_KEY] if PARAMETER_CONSTANT_CASEID_KEY in parameters else CASE_CONCEPT_NAME
    max_variants_to_return = parameters["max_variants_to_return"] if "max_variants_to_return" in parameters else None
    variants_df = parameters["variants_df"] if "variants_df" in parameters else get_variants_df(df,
                                                                                                parameters=parameters)
    variants_df = variants_df.reset_index()
    variants_list = variants_df.groupby("variant").agg("count").reset_index().to_dict('records')
    variants_list = sorted(variants_list, key=lambda x: x[case_id_glue], reverse=True)
    if max_variants_to_return:
        variants_list = variants_list[:min(len(variants_list), max_variants_to_return)]
    return variants_list


def get_variants_df_and_list(df, parameters=None):
    """
    (Technical method) Provides variants_df and variants_list out of the box

    Parameters
    ------------
    df
        Dataframe
    parameters
        Parameters of the algorithm, including:
            case_id_glue -> Column that contains the Case ID
            activity_key -> Column that contains the activity

    Returns
    ------------
    variants_df
        Variants dataframe
    variants_list
        List of variants sorted by their count
    """
    if parameters is None:
        parameters = {}
    case_id_glue = parameters[
        PARAMETER_CONSTANT_CASEID_KEY] if PARAMETER_CONSTANT_CASEID_KEY in parameters else CASE_CONCEPT_NAME
    variants_df = get_variants_df(df, parameters=parameters)
    parameters["variants_df"] = variants_df
    variants_stats = get_variant_statistics(df, parameters=parameters)
    variants_list = []
    for vd in variants_stats:
        variant = vd["variant"]
        count = vd[case_id_glue]
        variants_list.append([variant, count])
        variants_list = sorted(variants_list, key=lambda x: (x[1], x[0]), reverse=True)
    return variants_df, variants_list


def get_cases_description(df, parameters=None):
    """
    Get a description of traces present in the Pandas dataframe

    Parameters
    -----------
    df
        Pandas dataframe
    parameters
        Parameters of the algorithm, including:
            case_id_glue -> Column that identifies the case ID
            timestamp_key -> Column that identifies the timestamp
            enable_sort -> Enable sorting of traces
            sort_by_column -> Sort traces inside the dataframe using the specified column.
            Admitted values: startTime, endTime, caseDuration
            sort_ascending -> Set sort direction (boolean; it true then the sort direction is ascending,
            otherwise descending)
            max_ret_cases -> Set the maximum number of returned traces

    Returns
    -----------
    ret
        Dictionary of traces associated to their start timestamp, their end timestamp and their duration
    """
    if parameters is None:
        parameters = {}

    case_id_glue = parameters[
        PARAMETER_CONSTANT_CASEID_KEY] if PARAMETER_CONSTANT_CASEID_KEY in parameters else CASE_CONCEPT_NAME
    timestamp_key = parameters[
        PARAMETER_CONSTANT_TIMESTAMP_KEY] if PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else DEFAULT_TIMESTAMP_KEY
    enable_sort = parameters["enable_sort"] if "enable_sort" in parameters else True
    sort_by_column = parameters["sort_by_column"] if "sort_by_column" in parameters else "startTime"
    sort_ascending = parameters["sort_ascending"] if "sort_ascending" in parameters else True
    max_ret_cases = parameters["max_ret_cases"] if "max_ret_cases" in parameters else None

    grouped_df = df[[case_id_glue, timestamp_key]].groupby(df[case_id_glue])
    first_eve_df = grouped_df.first()
    last_eve_df = grouped_df.last()
    del grouped_df
    last_eve_df.columns = [str(col) + '_2' for col in first_eve_df.columns]
    stacked_df = pd.concat([first_eve_df, last_eve_df], axis=1)
    del first_eve_df
    del last_eve_df
    del stacked_df[case_id_glue]
    del stacked_df[case_id_glue + "_2"]
    stacked_df['caseDuration'] = stacked_df[timestamp_key + "_2"] - stacked_df[timestamp_key]
    stacked_df['caseDuration'] = stacked_df['caseDuration'].astype('timedelta64[s]')
    stacked_df[timestamp_key + "_2"] = stacked_df[timestamp_key + "_2"].astype('int64') // 10 ** 9
    stacked_df[timestamp_key] = stacked_df[timestamp_key].astype('int64') // 10 ** 9
    stacked_df = stacked_df.rename(columns={timestamp_key: 'startTime', timestamp_key + "_2": 'endTime'})
    if enable_sort:
        stacked_df = stacked_df.sort_values(sort_by_column, ascending=sort_ascending)

    if max_ret_cases is not None:
        stacked_df = stacked_df.head(n=min(max_ret_cases, len(stacked_df)))
    ret = stacked_df.to_dict('index')
    return ret


def get_variants_df(df, parameters=None):
    """
    Get variants dataframe from a Pandas dataframe

    Parameters
    -----------
    df
        Dataframe
    parameters
        Parameters of the algorithm, including:
            case_id_glue -> Column that contains the Case ID
            activity_key -> Column that contains the activity

    Returns
    -----------
    variants_df
        Variants dataframe
    """
    if parameters is None:
        parameters = {}

    case_id_glue = parameters[
        PARAMETER_CONSTANT_CASEID_KEY] if PARAMETER_CONSTANT_CASEID_KEY in parameters else CASE_CONCEPT_NAME
    activity_key = parameters[
        PARAMETER_CONSTANT_ACTIVITY_KEY] if PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY

    return df.groupby(case_id_glue)[activity_key].agg({'variant': lambda col: ','.join(col)})


def get_events(df, case_id, parameters=None):
    """
    Get events belonging to the specified case

    Parameters
    -----------
    df
        Pandas dataframe
    case_id
        Required case ID
    parameters
        Possible parameters of the algorithm, including:
            case_id_glue -> Column in which the case ID is contained

    Returns
    ----------
    list_eve
        List of events belonging to the case
    """
    if parameters is None:
        parameters = {}
    case_id_glue = parameters[
        PARAMETER_CONSTANT_CASEID_KEY] if PARAMETER_CONSTANT_CASEID_KEY in parameters else CASE_CONCEPT_NAME
    return df[df[case_id_glue] == case_id].to_dict('records')


def get_kde_caseduration(df, parameters=None):
    """
    Gets the estimation of KDE density for the case durations calculated on the dataframe

    Parameters
    --------------
    df
        Pandas dataframe
    parameters
        Possible parameters of the algorithm, including:
            graph_points -> number of points to include in the graph
            case_id_glue -> Column hosting the Case ID


    Returns
    --------------
    x
        X-axis values to represent
    y
        Y-axis values to represent
    """
    cases = get_cases_description(df, parameters=parameters)
    duration_values = [x["caseDuration"] for x in cases.values()]

    return case_duration_commons.get_kde_caseduration(duration_values, parameters=parameters)

def get_kde_caseduration_json(df, parameters=None):
    """
    Gets the estimation of KDE density for the case durations calculated on the log/dataframe
    (expressed as JSON)

    Parameters
    --------------
    df
        Pandas dataframe
    parameters
        Possible parameters of the algorithm, including:
            graph_points -> number of points to include in the graph
            case_id_glue -> Column hosting the Case ID

    Returns
    --------------
    json
        JSON representing the graph points
    """
    cases = get_cases_description(df, parameters=parameters)
    duration_values = [x["caseDuration"] for x in cases.values()]

    return case_duration_commons.get_kde_caseduration_json(duration_values, parameters=parameters)

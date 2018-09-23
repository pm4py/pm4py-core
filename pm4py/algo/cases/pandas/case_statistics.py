import pandas as pd
from pm4py.entities.log.util import xes
from pm4py.util import constants
from pm4py.algo.filtering.common import filtering_constants

def get_variants_statistics(df, parameters=None):
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
    case_id_glue = parameters[constants.PARAMETER_CONSTANT_CASEID_KEY] if constants.PARAMETER_CONSTANT_CASEID_KEY in parameters else filtering_constants.CASE_CONCEPT_NAME
    max_variants_to_return = parameters["max_variants_to_return"] if "max_variants_to_return" in parameters else None
    variants_df = parameters["variants_df"] if "variants_df" in parameters else get_variants_df(df, parameters=parameters)
    variants_df = variants_df.reset_index()
    variantsList = variants_df.groupby("variant").agg("count").reset_index().to_dict('records')
    variantsList = sorted(variantsList, key=lambda x: x[case_id_glue], reverse=True)
    if max_variants_to_return:
        variantsList = variantsList[:min(len(variantsList), max_variants_to_return)]
    return variantsList

def get_cases_description(df, parameters=None):
    """
    Get a description of cases present in the Pandas dataframe

    Parameters
    -----------
    df
        Pandas dataframe
    parameters
        Parameters of the algorithm, including:
            case_id_glue -> Column that identifies the case ID
            timestamp_key -> Column that identifies the timestamp
            enable_sort -> Enable sorting of cases
            sort_by_column -> Sort cases inside the dataframe using the specified column. Admitted values: startTime, endTime, caseDuration
            sort_ascending -> Set sort direction (boolean; it true then the sort direction is ascending, otherwise descending)
            max_ret_cases -> Set the maximum number of returned cases

    Returns
    -----------
    ret
        Dictionary of cases associated to their start timestamp, their end timestamp and their duration
    """
    if parameters is None:
        parameters = {}

    case_id_glue = parameters[constants.PARAMETER_CONSTANT_CASEID_KEY] if constants.PARAMETER_CONSTANT_CASEID_KEY in parameters else filtering_constants.CASE_CONCEPT_NAME
    timestamp_key = parameters[constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] if constants.PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else xes.DEFAULT_TIMESTAMP_KEY
    enable_sort = parameters["enable_sort"] if "enable_sort" in parameters else True
    sort_by_column = parameters["sort_by_column"] if "sort_by_column" in parameters else "startTime"
    sort_ascending = parameters["sort_ascending"] if "sort_ascending" in parameters else "ascending"
    max_ret_cases = parameters["max_ret_cases"] if "max_ret_cases" in parameters else None

    groupedDf = df[[case_id_glue, timestamp_key]].groupby(df[case_id_glue])
    firstEveDf = groupedDf.first()
    lastEveDf = groupedDf.last()
    del groupedDf
    lastEveDf.columns = [str(col) + '_2' for col in firstEveDf.columns]
    stackedDf = pd.concat([firstEveDf, lastEveDf], axis=1)
    del firstEveDf
    del lastEveDf
    del stackedDf[case_id_glue]
    del stackedDf[case_id_glue+"_2"]
    stackedDf['caseDuration'] = stackedDf[timestamp_key + "_2"] - stackedDf[timestamp_key]
    stackedDf['caseDuration'] = stackedDf['caseDuration'].astype('timedelta64[s]')
    stackedDf[timestamp_key + "_2"] = stackedDf[timestamp_key + "_2"].astype('int64')//10**9
    stackedDf[timestamp_key] = stackedDf[timestamp_key].astype('int64')//10**9
    stackedDf = stackedDf.rename(columns={timestamp_key: 'startTime', timestamp_key+"_2": 'endTime'})
    if enable_sort:
        stackedDf = stackedDf.sort_values(sort_by_column, ascending=sort_ascending)

    if max_ret_cases is not None:
        stackedDf = stackedDf.head(n=min(max_ret_cases, len(stackedDf)))
    ret = stackedDf.to_dict('index')
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

    case_id_glue = parameters[constants.PARAMETER_CONSTANT_CASEID_KEY] if constants.PARAMETER_CONSTANT_CASEID_KEY in parameters else filtering_constants.CASE_CONCEPT_NAME
    activity_key = parameters[constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY

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
    case_id_glue = parameters[constants.PARAMETER_CONSTANT_CASEID_KEY] if constants.PARAMETER_CONSTANT_CASEID_KEY in parameters else filtering_constants.CASE_CONCEPT_NAME
    return df[df[case_id_glue] == case_id].to_dict('records')
import pandas as pd

def filter_df_on_ncases(df, case_id_glue="case:concept:name", max_no_cases=1000):
    """
    Filter a dataframe keeping only the specified maximum number of cases

    Parameters
    -----------
    df
        Dataframe
    case_id_glue
        Case ID column in the CSV
    max_no_cases
        Maximum number of cases to keep

    Returns
    ------------
    df
        Filtered dataframe
    """
    cases_values_dict = dict(df[case_id_glue].value_counts())
    cases_to_keep = []
    for case in cases_values_dict:
        cases_to_keep.append(case)
    cases_to_keep = cases_to_keep[0:min(len(cases_to_keep),max_no_cases)]
    df = df[df[case_id_glue].isin(cases_to_keep)]
    return df

def filter_df_on_case_size(df, case_id_glue="case:concept:name", min_case_size=2, max_case_size=None):
    """
    Filter a dataframe keeping only cases with at least the specified number of events

    Parameters
    -----------
    df
        Dataframe
    case_id_glue
        Case ID column in the CSV
    max_no_cases
        Maximum number of cases to keep

    Returns
    -----------
    df
        Filtered dataframe
    """
    element_group_size = df[case_id_glue].groupby(df[case_id_glue]).transform('size')
    if max_case_size:
        return df[element_group_size > min_case_size and element_group_size < max_case_size]
    return df[element_group_size > min_case_size]

def filter_df_on_case_performance(df, case_id_glue="case:concept:name", timestamp_key="time:timestamp", min_case_performance=0, max_case_performance=10000000000):
    """
    Filter a dataframe on case performance

    Parameters
    -----------
    df
        Dataframe
    case_id_glue
        Case ID column in the CSV
    timestamp_key
        Timestamp column to use for the CSV
    min_case_performance
        Minimum case performance
    max_case_performance
        Maximum case performance

    Returns
    -----------
    df
        Filtered dataframe
    """
    groupedDf = df[[case_id_glue, timestamp_key]].groupby(df[case_id_glue])
    startEvents = groupedDf.first()
    endEvents = groupedDf.last()
    endEvents.columns = [str(col) + '_2' for col in endEvents.columns]
    stackedDf = pd.concat([startEvents, endEvents], axis=1)
    stackedDf['caseDuration'] = stackedDf[timestamp_key + "_2"] - stackedDf[timestamp_key]
    stackedDf['caseDuration'] = stackedDf['caseDuration'].astype('timedelta64[s]')
    stackedDf = stackedDf[stackedDf['caseDuration'] < max_case_performance]
    stackedDf = stackedDf[stackedDf['caseDuration'] > min_case_performance]
    i1 = df.set_index(case_id_glue).index
    i2 = stackedDf.set_index(case_id_glue).index
    return df[i1.isin(i2)]
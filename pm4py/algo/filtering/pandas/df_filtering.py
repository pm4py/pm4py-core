import pandas as pd

def filter_df_keeping_specno_activities(df, activity_key="concept:name", max_no_activities=25):
    """
    Filter a dataframe on the specified number of attributes

    Parameters
    -----------
    df
        Dataframe
    activity_key
        Activity key in dataframe (must be specified if different from concept:name)
    max_no_activities
        Maximum allowed number of attributes

    Returns
    ------------
    df
        Filtered dataframe
    """
    activity_values_dict = dict(df[activity_key].value_counts())
    activity_values_ordered_list = []
    for act in activity_values_dict:
        activity_values_ordered_list.append([act, activity_values_dict[act]])
    activity_values_ordered_list = sorted(activity_values_ordered_list)
    # keep only a number of attributes <= max_no_activities
    activity_values_ordered_list = activity_values_ordered_list[0:min(len(activity_values_ordered_list), max_no_activities)]
    activity_to_keep = [x[0] for x in activity_values_ordered_list]
    df = df[df[activity_key].isin(activity_to_keep)]
    return df

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

def filter_df_on_attribute_values(df, case_id_glue="case:concept:name", attribute_key="concept:name", values=None, positive=True):
    """
    Filter dataframe on attribute values

    Parameters
    ----------
    df
        Dataframe
    case_id_glue
        Case ID column in the dataframe
    attribute_key
        Attribute we want to filter
    values
        Values to filter on
    positive
        Specifies if the filtered should be applied including traces (positive=True) or excluding traces (positive=False)

    Returns
    ----------
    df
        Filtered dataframe
    """
    if values is None:
        values = []
    filteredDfByEv = df[df[attribute_key].isin(values)]
    i1 = df.set_index(case_id_glue).index
    i2 = filteredDfByEv.set_index(case_id_glue).index
    if positive:
        return df[i1.isin(i2)]
    return df[~i1.isin(i2)]
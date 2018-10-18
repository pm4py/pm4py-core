import pandas as pd


def filter_on_ncases(df, case_id_glue="case:concept:name", max_no_cases=1000):
    """
    Filter a dataframe keeping only the specified maximum number of traces

    Parameters
    -----------
    df
        Dataframe
    case_id_glue
        Case ID column in the CSV
    max_no_cases
        Maximum number of traces to keep

    Returns
    ------------
    df
        Filtered dataframe
    """
    cases_values_dict = dict(df[case_id_glue].value_counts())
    cases_to_keep = []
    for case in cases_values_dict:
        cases_to_keep.append(case)
    cases_to_keep = cases_to_keep[0:min(len(cases_to_keep), max_no_cases)]
    df = df[df[case_id_glue].isin(cases_to_keep)]
    return df


def filter_on_case_size(df, case_id_glue="case:concept:name", min_case_size=2, max_case_size=None):
    """
    Filter a dataframe keeping only traces with at least the specified number of events

    Parameters
    -----------
    df
        Dataframe
    case_id_glue
        Case ID column in the CSV
    min_case_size
        Minimum size of a case
    max_case_size
        Maximum case size

    Returns
    -----------
    df
        Filtered dataframe
    """
    element_group_size = df[case_id_glue].groupby(df[case_id_glue]).transform('size')
    if max_case_size:
        return df[min_case_size <= element_group_size <= max_case_size]
    return df[element_group_size >= min_case_size]


def filter_on_case_performance(df, case_id_glue="case:concept:name", timestamp_key="time:timestamp",
                               min_case_performance=0, max_case_performance=10000000000):
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
    grouped_df = df[[case_id_glue, timestamp_key]].groupby(df[case_id_glue])
    start_events = grouped_df.first()
    end_events = grouped_df.last()
    end_events.columns = [str(col) + '_2' for col in end_events.columns]
    stacked_df = pd.concat([start_events, end_events], axis=1)
    stacked_df['caseDuration'] = stacked_df[timestamp_key + "_2"] - stacked_df[timestamp_key]
    stacked_df['caseDuration'] = stacked_df['caseDuration'].astype('timedelta64[s]')
    stacked_df = stacked_df[stacked_df['caseDuration'] < max_case_performance]
    stacked_df = stacked_df[stacked_df['caseDuration'] > min_case_performance]
    i1 = df.set_index(case_id_glue).index
    i2 = stacked_df.set_index(case_id_glue).index
    return df[i1.isin(i2)]


def apply(df, parameters=None):
    del df
    del parameters
    raise Exception("apply method not available for case filter")


def apply_auto_filter(df, parameters=None):
    del df
    del parameters
    raise Exception("apply_auto_filter method not available for case filter")

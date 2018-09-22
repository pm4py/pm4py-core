import pandas as pd

def get_cases_description(df, case_id_glue="case:concept:name", timestamp_key="time:timestamp", enable_sort=True, sort_by_column="startTime", sort_ascending=True, max_ret_cases=None):
    """
    Get a description of cases present in the Pandas dataframe

    Parameters
    -----------
    df
        Pandas dataframe
    case_id_glue
        Column that identifies the case ID
    timestamp_key
        Column that identifies the timestamp
    enable_sort
        Enable sorting of cases
    sort_by_column
        Sort cases inside the dataframe using the specified column. Admitted values: startTime, endTime, caseDuration
    sort_ascending
        Set sort direction (boolean; it true then the sort direction is ascending, otherwise descending)
    max_ret_cases
        Set the maximum number of returned cases

    Returns
    -----------
    ret
        Dictionary of cases associated to their start timestamp, their end timestamp and their duration
    """
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
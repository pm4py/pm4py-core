import pandas as pd
from collections import Counter
from statistics import mean
import numpy as np

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

def get_dfg_graph(df, measure="frequency", activity_key="concept:name", case_id_glue="case:concept:name", timestamp_key="time:timestamp", perf_aggregation_key="mean"):
    """
    Get DFG graph from Pandas dataframe

    Parameters
    -----------
    df
        Dataframe
    measure
        Measure to use (frequency/performance/both)
    activity_key
        Activity key to use in the grouping
    case_id_glue
        Case ID identifier
    timestamp_key
        Timestamp key
    perf_aggregation_key
        Performance aggregation key (mean, median, min, max)

    Returns
    -----------
    dfg
        DFG in the chosen measure (may be only the frequency, only the performance, or both)
    """
    # to get rows belonging to same case ID together, we need to sort on case ID
    df = df.sort_values([case_id_glue, timestamp_key])
    # to test approaches reduce dataframe to case, activity and complete timestamp columns
    dfReduced = df[[case_id_glue, activity_key, timestamp_key]]
    # shift the dataframe by 1, in order to couple successive rows
    dfReducedShifted = dfReduced.shift(-1)
    # change column names to shifted dataframe
    dfReducedShifted.columns = [str(col) + '_2' for col in dfReducedShifted.columns]
    # concate the two dataframe to get a unique dataframe
    dfSuccessiveRows = pd.concat([dfReduced, dfReducedShifted], axis=1)
    # as successive rows in the sorted dataframe may belong to different case IDs we have to restrict ourselves to successive
    # rows belonging to same case ID
    dfSuccessiveRows = dfSuccessiveRows[dfSuccessiveRows[case_id_glue] == dfSuccessiveRows[case_id_glue+'_2']]

    # calculate the difference between the timestamps of two successive events
    dfSuccessiveRows['caseDuration'] = (dfSuccessiveRows[timestamp_key+'_2'] - dfSuccessiveRows[timestamp_key]).apply(
        lambda x: x.total_seconds())
    # groups couple of attributes (directly follows relation, we can measure the frequency and the performance)
    directlyFollowsGrouping = dfSuccessiveRows.groupby([activity_key, activity_key+'_2'])['caseDuration']

    dfg_frequency = {}
    dfg_performance = {}

    if measure == "frequency" or measure == "both":
        dfg_frequency = directlyFollowsGrouping.size().to_dict()

    if measure == "performance" or measure == "both":
        dfg_performance = directlyFollowsGrouping.agg(perf_aggregation_key).to_dict()

    if measure == "frequency":
        return dfg_frequency

    if measure == "performance":
        return dfg_performance

    if measure == "both":
        return [dfg_frequency, dfg_performance]
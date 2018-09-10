import pandas as pd
from collections import Counter
from statistics import mean

def get_activities_count(df, activity_key="concept:name"):
    """
    Return list of activities contained in the specified column of the CSV

    Parameters
    -----------
    df
        Pandas dataframe
    activity_key
        Columns that is the activity

    Returns
    -----------
    activities_values_dict
        Activities in the specified column, along with their count
    """
    activity_values_dict = dict(df[activity_key].value_counts())
    return activity_values_dict

def get_dfg_graph(df, measure="frequency", activity_key="concept:name", case_id_glue="case:concept:name", timestamp_key="time:timestamp"):

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
    dfSuccessiveRows['timeDiff'] = (dfSuccessiveRows[timestamp_key+'_2'] - dfSuccessiveRows[timestamp_key]).apply(
        lambda x: x.total_seconds())
    # groups couple of activities (directly follows relation, we can measure the frequency and the performance)
    directlyFollowsGrouping = dfSuccessiveRows.groupby([activity_key, activity_key+'_2'])['timeDiff']

    dfg_frequency = {}
    dfg_performance = {}

    if measure == "frequency" or measure == "both":
        dfg_frequency = directlyFollowsGrouping.size().to_dict()

    if measure == "performance" or measure == "both":
        dfg_performance = directlyFollowsGrouping.agg('mean').to_dict()

    if measure == "frequency":
        return dfg_frequency

    if measure == "performance":
        return dfg_performance

    if measure == "both":
        return [dfg_frequency, dfg_performance]
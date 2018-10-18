import pandas as pd


def get_dfg_graph(df, measure="frequency", activity_key="concept:name", case_id_glue="case:concept:name",
                  timestamp_key="time:timestamp", perf_aggregation_key="mean", sort_required=True):
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
    sort_required
        Specify if a sort on the Case ID and the timestamp is required

    Returns
    -----------
    dfg
        DFG in the chosen measure (may be only the frequency, only the performance, or both)
    """
    if sort_required:
        # to get rows belonging to same case ID together, we need to sort on case ID
        df = df.sort_values([case_id_glue, timestamp_key])
    # to test approaches reduce dataframe to case, activity and complete timestamp columns
    df_reduced = df[[case_id_glue, activity_key, timestamp_key]]
    # shift the dataframe by 1, in order to couple successive rows
    df_reduced_shifted = df_reduced.shift(-1)
    # change column names to shifted dataframe
    df_reduced_shifted.columns = [str(col) + '_2' for col in df_reduced_shifted.columns]
    # concate the two dataframe to get a unique dataframe
    df_successive_rows = pd.concat([df_reduced, df_reduced_shifted], axis=1)
    # as successive rows in the sorted dataframe may belong to different case IDs we have to restrict ourselves to
    # successive rows belonging to same case ID
    df_successive_rows = df_successive_rows[df_successive_rows[case_id_glue] == df_successive_rows[case_id_glue + '_2']]

    # calculate the difference between the timestamps of two successive events
    df_successive_rows['caseDuration'] = (
            df_successive_rows[timestamp_key + '_2'] - df_successive_rows[timestamp_key]).astype('timedelta64[s]')
    # groups couple of attributes (directly follows relation, we can measure the frequency and the performance)
    directly_follows_grouping = df_successive_rows.groupby([activity_key, activity_key + '_2'])['caseDuration']

    dfg_frequency = {}
    dfg_performance = {}

    if measure == "frequency" or measure == "both":
        dfg_frequency = directly_follows_grouping.size().to_dict()

    if measure == "performance" or measure == "both":
        dfg_performance = directly_follows_grouping.agg(perf_aggregation_key).to_dict()

    if measure == "frequency":
        return dfg_frequency

    if measure == "performance":
        return dfg_performance

    if measure == "both":
        return [dfg_frequency, dfg_performance]

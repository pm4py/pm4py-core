from pm4py.util import xes_constants, pandas_utils, constants


def get_dfg_graph(df, measure="frequency", activity_key="concept:name", case_id_glue="case:concept:name",
                  start_timestamp_key=None, timestamp_key="time:timestamp", perf_aggregation_key="mean",
                  sort_caseid_required=True,
                  sort_timestamp_along_case_id=True, keep_once_per_case=False, window=1):
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
    start_timestamp_key
        Start timestamp key
    timestamp_key
        Timestamp key
    perf_aggregation_key
        Performance aggregation key (mean, median, min, max)
    sort_caseid_required
        Specify if a sort on the Case ID is required
    sort_timestamp_along_case_id
        Specifying if sorting by timestamp along the CaseID is required
    keep_once_per_case
        In the counts, keep only one occurrence of the path per case (the first)
    window
        Window of the DFG (default 1)

    Returns
    -----------
    dfg
        DFG in the chosen measure (may be only the frequency, only the performance, or both)
    """
    import pandas as pd

    # if not differently specified, set the start timestamp key to the timestamp key
    # to avoid retro-compatibility problems
    if start_timestamp_key is None:
        start_timestamp_key = xes_constants.DEFAULT_START_TIMESTAMP_KEY
        df[start_timestamp_key] = df[timestamp_key]

    # to get rows belonging to same case ID together, we need to sort on case ID
    if sort_caseid_required:
        if sort_timestamp_along_case_id:
            df = df.sort_values([case_id_glue, start_timestamp_key, timestamp_key])
        else:
            df = df.sort_values(case_id_glue)

    # to increase the speed of the approaches reduce dataframe to case, activity (and possibly complete timestamp)
    # columns
    if measure == "frequency":
        df_reduced = df[[case_id_glue, activity_key]]
    else:
        df_reduced = df[[case_id_glue, activity_key, start_timestamp_key, timestamp_key]]
    # shift the dataframe by 1, in order to couple successive rows
    df_reduced_shifted = df_reduced.shift(-window)
    # change column names to shifted dataframe
    df_reduced_shifted.columns = [str(col) + '_2' for col in df_reduced_shifted.columns]
    # concate the two dataframe to get a unique dataframe
    df_successive_rows = pd.concat([df_reduced, df_reduced_shifted], axis=1)
    # as successive rows in the sorted dataframe may belong to different case IDs we have to restrict ourselves to
    # successive rows belonging to same case ID
    df_successive_rows = df_successive_rows[df_successive_rows[case_id_glue] == df_successive_rows[case_id_glue + '_2']]
    if keep_once_per_case:
        df_successive_rows = df_successive_rows.groupby(
            [case_id_glue, activity_key, activity_key + "_2"]).first().reset_index()

    all_columns = set(df_successive_rows.columns)
    all_columns = list(all_columns - set([activity_key, activity_key + '_2']))

    if measure == "performance" or measure == "both":
        # calculate the difference between the timestamps of two successive events
        df_successive_rows[constants.DEFAULT_FLOW_TIME] = (
                df_successive_rows[start_timestamp_key + '_2'] - df_successive_rows[timestamp_key]).astype(
            'timedelta64[s]')
        # in the arc performance calculation, make sure to consider positive or null values
        df_successive_rows[constants.DEFAULT_FLOW_TIME] = df_successive_rows[constants.DEFAULT_FLOW_TIME].apply(
            lambda x: max(x, 0))
        # groups couple of attributes (directly follows relation, we can measure the frequency and the performance)
        directly_follows_grouping = df_successive_rows.groupby([activity_key, activity_key + '_2'])[
            constants.DEFAULT_FLOW_TIME]
    else:
        directly_follows_grouping = df_successive_rows.groupby([activity_key, activity_key + '_2'])
        if all_columns:
            directly_follows_grouping = directly_follows_grouping[all_columns[0]]

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


def get_freq_triples(df, activity_key="concept:name", case_id_glue="case:concept:name", timestamp_key="time:timestamp",
                     sort_caseid_required=True, sort_timestamp_along_case_id=True):
    """
    Gets the frequency triples out of a dataframe

    Parameters
    ------------
    df
        Dataframe
    activity_key
        Activity key
    case_id_glue
        Case ID glue
    timestamp_key
        Timestamp key
    sort_caseid_required
        Determine if sort by case ID is required (default: True)
    sort_timestamp_along_case_id
        Determine if sort by timestamp is required (default: True)

    Returns
    -------------
    freq_triples
        Frequency triples from the dataframe
    """
    import pandas as pd

    if sort_caseid_required:
        if sort_timestamp_along_case_id:
            df = df.sort_values([case_id_glue, timestamp_key])
        else:
            df = df.sort_values(case_id_glue)
    df_reduced = df[[case_id_glue, activity_key]]
    # shift the dataframe by 1
    df_reduced_1 = df_reduced.shift(-1)
    # shift the dataframe by 2
    df_reduced_2 = df_reduced.shift(-2)
    # change column names to shifted dataframe
    df_reduced_1.columns = [str(col) + '_2' for col in df_reduced_1.columns]
    df_reduced_2.columns = [str(col) + '_3' for col in df_reduced_2.columns]

    df_successive_rows = pd.concat([df_reduced, df_reduced_1, df_reduced_2], axis=1)
    df_successive_rows = df_successive_rows[df_successive_rows[case_id_glue] == df_successive_rows[case_id_glue + '_2']]
    df_successive_rows = df_successive_rows[df_successive_rows[case_id_glue] == df_successive_rows[case_id_glue + '_3']]
    all_columns = set(df_successive_rows.columns)
    all_columns = list(all_columns - set([activity_key, activity_key + '_2', activity_key + '_3']))
    directly_follows_grouping = df_successive_rows.groupby([activity_key, activity_key + '_2', activity_key + '_3'])
    if all_columns:
        directly_follows_grouping = directly_follows_grouping[all_columns[0]]
    freq_triples = directly_follows_grouping.size().to_dict()
    return freq_triples


def get_partial_order_dataframe(df, start_timestamp_key=None, timestamp_key="time:timestamp",
                                case_id_glue="case:concept:name", activity_key="concept:name", sort_caseid_required=True,
                                sort_timestamp_along_case_id=True, reduce_dataframe=True, keep_first_following=True):
    """
    Gets the partial order between events (of the same case) in a Pandas dataframe

    Parameters
    --------------
    df
        Dataframe
    start_timestamp_key
        Start timestamp key (if not provided, defaulted to the timestamp_key)
    timestamp_key
        Complete timestamp
    case_id_glue
        Column of the dataframe to use as case ID
    activity_key
        Activity key
    sort_caseid_required
        Tells if a sort by case ID is required (default: True)
    sort_timestamp_along_case_id
        Tells if a sort by timestamp is required along the case ID (default: True)
    reduce_dataframe
        To fasten operation, keep only essential columns in the dataframe
    keep_first_following
        Keep only the first event following the given event
    Returns
    ---------------
    part_ord_dataframe
        Partial order dataframe (with @@flow_time between events)
    """
    # if not differently specified, set the start timestamp key to the timestamp key
    # to avoid retro-compatibility problems
    if start_timestamp_key is None:
        start_timestamp_key = xes_constants.DEFAULT_START_TIMESTAMP_KEY
        df[start_timestamp_key] = df[timestamp_key]

    # to get rows belonging to same case ID together, we need to sort on case ID
    if sort_caseid_required:
        if sort_timestamp_along_case_id:
            df = df.sort_values([case_id_glue, start_timestamp_key, timestamp_key])
        else:
            df = df.sort_values(case_id_glue)

    # to increase the speed of the approaches reduce dataframe to case, activity (and possibly complete timestamp)
    # columns
    if reduce_dataframe:
        df = df[[case_id_glue, activity_key, start_timestamp_key, timestamp_key]]

    df = pandas_utils.insert_index(df)
    df = df.set_index(case_id_glue)
    df_copy = df.copy()

    df = df.join(df_copy, rsuffix="_2").dropna()
    df = df[df[constants.DEFAULT_INDEX_KEY] < df[constants.DEFAULT_INDEX_KEY + "_2"]]
    df = df[df[timestamp_key] <= df[start_timestamp_key + "_2"]]
    df = df.reset_index()

    df[constants.DEFAULT_FLOW_TIME] = (df[start_timestamp_key + "_2"] - df[timestamp_key]).astype('timedelta64[s]')

    if keep_first_following:
        df = df.groupby(constants.DEFAULT_INDEX_KEY).first().reset_index()

    return df


def get_concurrent_events_dataframe(df, start_timestamp_key=None, timestamp_key="time:timestamp",
                                    case_id_glue="case:concept:name", activity_key="concept:name", sort_caseid_required=True,
                                    sort_timestamp_along_case_id=True, reduce_dataframe=True,
                                    max_start_column="@@max_start_column", min_complete_column="@@min_complete_column",
                                    diff_maxs_minc="@@diff_maxs_minc"):
    """
    Gets the concurrent events (of the same case) in a Pandas dataframe

    Parameters
    --------------
    df
        Dataframe
    start_timestamp_key
        Start timestamp key (if not provided, defaulted to the timestamp_key)
    timestamp_key
        Complete timestamp
    case_id_glue
        Column of the dataframe to use as case ID
    activity_key
        Activity key
    sort_caseid_required
        Tells if a sort by case ID is required (default: True)
    sort_timestamp_along_case_id
        Tells if a sort by timestamp is required along the case ID (default: True)
    reduce_dataframe
        To fasten operation, keep only essential columns in the dataframe
    Returns
    ---------------
    conc_ev_dataframe
        Concurrent events dataframe (with @@diff_maxs_minc as the size of the intersection of the intervals)
    """
    # if not differently specified, set the start timestamp key to the timestamp key
    # to avoid retro-compatibility problems
    if start_timestamp_key is None:
        start_timestamp_key = xes_constants.DEFAULT_START_TIMESTAMP_KEY
        df[start_timestamp_key] = df[timestamp_key]

    # to get rows belonging to same case ID together, we need to sort on case ID
    if sort_caseid_required:
        if sort_timestamp_along_case_id:
            df = df.sort_values([case_id_glue, start_timestamp_key, timestamp_key])
        else:
            df = df.sort_values(case_id_glue)

    # to increase the speed of the approaches reduce dataframe to case, activity (and possibly complete timestamp)
    # columns
    if reduce_dataframe:
        df = df[[case_id_glue, activity_key, start_timestamp_key, timestamp_key]]

    df = pandas_utils.insert_index(df)
    df = df.set_index(case_id_glue)
    df_copy = df.copy()

    df = df.join(df_copy, rsuffix="_2").dropna()
    df = df[df[constants.DEFAULT_INDEX_KEY] < df[constants.DEFAULT_INDEX_KEY + "_2"]]
    df[max_start_column] = df[[start_timestamp_key, start_timestamp_key + '_2']].max(axis=1)
    df[min_complete_column] = df[[timestamp_key, timestamp_key + '_2']].min(axis=1)
    df[max_start_column] = df[max_start_column].apply(lambda x: x.timestamp())
    df[min_complete_column] = df[min_complete_column].apply(lambda x: x.timestamp())
    df[diff_maxs_minc] = df[min_complete_column] - df[max_start_column]
    df = df[df[diff_maxs_minc] >= 0]

    return df

'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
from pm4py.util import xes_constants, pandas_utils, constants
from pm4py.util.business_hours import soj_time_business_hours_diff


def get_dfg_graph(df, measure="frequency", activity_key="concept:name", case_id_glue="case:concept:name",
                  start_timestamp_key=None, timestamp_key="time:timestamp", perf_aggregation_key="mean",
                  sort_caseid_required=True,
                  sort_timestamp_along_case_id=True, keep_once_per_case=False, window=1,
                  business_hours=False, business_hours_slot=None, workcalendar=constants.DEFAULT_BUSINESS_HOURS_WORKCALENDAR, target_activity_key=None,
                  reduce_columns=True, cost_attribute=None):
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

    # added support to specify an activity key for the target event which is different
    # from the activity key of the source event.
    if target_activity_key is None:
        target_activity_key = activity_key

    # if not differently specified, set the start timestamp key to the timestamp key
    # to avoid retro-compatibility problems
    st_eq_ct = start_timestamp_key == timestamp_key
    if start_timestamp_key is None:
        start_timestamp_key = xes_constants.DEFAULT_START_TIMESTAMP_KEY
        if start_timestamp_key not in df.columns:
            df[start_timestamp_key] = df[timestamp_key]
        st_eq_ct = True

    # to increase the speed of the approaches reduce dataframe to case, activity (and possibly complete timestamp)
    # columns
    if reduce_columns:
        red_attrs = {case_id_glue, activity_key, target_activity_key}
        if measure == "frequency" and not sort_timestamp_along_case_id:
            pass
        else:
            red_attrs.add(start_timestamp_key)
            red_attrs.add(timestamp_key)

        if measure == "cost":
            red_attrs.add(cost_attribute)

        df = df[list(red_attrs)]

    if measure == "cost":
        df[cost_attribute] = df[cost_attribute].fillna(value=0)

    # to get rows belonging to same case ID together, we need to sort on case ID
    if sort_caseid_required:
        if sort_timestamp_along_case_id:
            df = df.sort_values([case_id_glue, start_timestamp_key, timestamp_key])
        else:
            df = df.sort_values(case_id_glue)

    # shift the dataframe by 1, in order to couple successive rows
    df_shifted = df.shift(-window)
    # change column names to shifted dataframe
    df_shifted.columns = [str(col) + '_2' for col in df_shifted.columns]
    # concate the two dataframe to get a unique dataframe
    df_successive_rows = pandas_utils.concat([df, df_shifted], axis=1)
    # as successive rows in the sorted dataframe may belong to different case IDs we have to restrict ourselves to
    # successive rows belonging to same case ID
    df_successive_rows = df_successive_rows[df_successive_rows[case_id_glue] == df_successive_rows[case_id_glue + '_2']]
    if keep_once_per_case:
        df_successive_rows = df_successive_rows.groupby(
            [case_id_glue, activity_key, target_activity_key + "_2"]).first().reset_index()

    all_columns = set(df_successive_rows.columns)
    all_columns = list(all_columns - set([activity_key, target_activity_key + '_2']))

    if measure == "performance" or measure == "both":
        if not st_eq_ct:
            # in the arc performance calculation, make sure to consider positive or null values
            df_successive_rows[start_timestamp_key + '_2'] = df_successive_rows[[start_timestamp_key + '_2', timestamp_key]].max(axis=1)
        
        # calculate the difference between the timestamps of two successive events
        if business_hours:
            if business_hours_slot is None:
                business_hours_slot = constants.DEFAULT_BUSINESS_HOUR_SLOTS
            df_successive_rows[constants.DEFAULT_FLOW_TIME] = df_successive_rows.apply(
            lambda x: soj_time_business_hours_diff(x[timestamp_key], x[start_timestamp_key + '_2'], business_hours_slot, workcalendar), axis=1)
        else:
            difference = df_successive_rows[start_timestamp_key + '_2'] - df_successive_rows[timestamp_key]
            df_successive_rows[constants.DEFAULT_FLOW_TIME] = pandas_utils.get_total_seconds(difference)
        # groups couple of attributes (directly follows relation, we can measure the frequency and the performance)
        directly_follows_grouping = df_successive_rows.groupby([activity_key, target_activity_key + '_2'])[
            constants.DEFAULT_FLOW_TIME]
    elif measure == "cost":
        directly_follows_grouping = df_successive_rows.groupby([activity_key, target_activity_key + '_2'])[cost_attribute + '_2']
    else:
        directly_follows_grouping = df_successive_rows.groupby([activity_key, target_activity_key + '_2'])
        if all_columns:
            directly_follows_grouping = directly_follows_grouping[all_columns[0]]

    dfg_frequency = {}
    dfg_performance = {}

    if measure == "frequency" or measure == "both":
        dfg_frequency = directly_follows_grouping.size().to_dict()

    if measure == "performance" or measure == "cost" or measure == "both":
        if perf_aggregation_key == "all":
            dfg_performance_mean = directly_follows_grouping.agg("mean").to_dict()
            dfg_performance_median = directly_follows_grouping.agg("median").to_dict()
            dfg_performance_max = directly_follows_grouping.agg("max").to_dict()
            dfg_performance_min = directly_follows_grouping.agg("min").to_dict()
            dfg_performance_sum = directly_follows_grouping.agg("sum").to_dict()
            dfg_performance_std = directly_follows_grouping.agg("std").to_dict()
            dfg_performance = {}
            for key in dfg_performance_mean:
                dfg_performance[key] = {"mean": dfg_performance_mean[key], "median": dfg_performance_median[key], "max": dfg_performance_max[key], "min": dfg_performance_min[key], "sum": dfg_performance_sum[key], "stdev": dfg_performance_std[key]}
        elif perf_aggregation_key == "raw_values":
            dfg_performance = directly_follows_grouping.agg(list).to_dict()
        else:
            dfg_performance = directly_follows_grouping.agg(perf_aggregation_key).to_dict()

    if measure == "frequency":
        return dfg_frequency

    if measure == "performance" or measure == "cost":
        return dfg_performance

    if measure == "both":
        return [dfg_frequency, dfg_performance]


def get_partial_order_dataframe(df, start_timestamp_key=None, timestamp_key="time:timestamp",
                                case_id_glue="case:concept:name", activity_key="concept:name",
                                sort_caseid_required=True,
                                sort_timestamp_along_case_id=True, reduce_dataframe=True, keep_first_following=True,
                                business_hours=False, business_hours_slot=None, workcalendar=constants.DEFAULT_BUSINESS_HOURS_WORKCALENDAR,
                                event_index=constants.DEFAULT_INDEX_KEY):
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

    if start_timestamp_key not in df:
        df[start_timestamp_key] = df[timestamp_key]

    # to increase the speed of the approaches reduce dataframe to case, activity (and possibly complete timestamp)
    # columns
    if reduce_dataframe:
        needed_columns = {case_id_glue, activity_key, start_timestamp_key, timestamp_key}
        if event_index in df.columns:
            needed_columns.add(event_index)
        needed_columns = list(needed_columns)
        df = df[needed_columns]

    # to get rows belonging to same case ID together, we need to sort on case ID
    if sort_caseid_required:
        if sort_timestamp_along_case_id:
            df = df.sort_values([case_id_glue, start_timestamp_key, timestamp_key])
        else:
            df = df.sort_values(case_id_glue)
        df = df.reset_index(drop=True)

    if event_index not in df.columns:
        df = pandas_utils.insert_index(df, event_index, copy_dataframe=False, reset_index=False)

    df = df.set_index(case_id_glue)

    df = df.join(df, rsuffix="_2")
    df = df[df[event_index] < df[event_index + "_2"]]
    df = df[df[timestamp_key] <= df[start_timestamp_key + '_2']]

    df = df.reset_index()

    if business_hours:
        if business_hours_slot is None:
            business_hours_slot = constants.DEFAULT_BUSINESS_HOUR_SLOTS
        df[constants.DEFAULT_FLOW_TIME] = df.apply(
            lambda x: soj_time_business_hours_diff(x[timestamp_key], x[start_timestamp_key + '_2'], business_hours_slot, workcalendar), axis=1)
    else:
        df[constants.DEFAULT_FLOW_TIME] = pandas_utils.get_total_seconds(df[start_timestamp_key + "_2"] - df[timestamp_key])

    if keep_first_following:
        df = df.groupby(constants.DEFAULT_INDEX_KEY).first().reset_index()

    return df


def get_concurrent_events_dataframe(df, start_timestamp_key=None, timestamp_key="time:timestamp",
                                    case_id_glue="case:concept:name", activity_key="concept:name",
                                    sort_caseid_required=True,
                                    sort_timestamp_along_case_id=True, reduce_dataframe=True,
                                    max_start_column="@@max_start_column", min_complete_column="@@min_complete_column",
                                    diff_maxs_minc="@@diff_maxs_minc", strict=False):
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
    strict
        Gets only entries that are strictly concurrent (i.e. the length of the intersection as real interval is > 0)

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
    if strict:
        df = df[df[diff_maxs_minc] > 0]
    else:
        df = df[df[diff_maxs_minc] >= 0]

    return df

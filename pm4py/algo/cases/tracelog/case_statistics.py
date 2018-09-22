def get_cases_description(trace_log, case_id_key="concept:name", timestamp_key="time:timestamp", enable_sort=True, sort_by_index=1, sort_ascending=True, max_ret_cases=None):
    """
    Get a description of cases present in the trace log

    Parameters
    -----------
    trace_log
        Trace log
    case_id_key
        Trace attribute in which the case ID is contained
    timestamp_key
        Column that identifies the timestamp
    enable_sort
        Enable sorting of cases
    sort_by_index
        Sort the cases using this index:
            0 -> case ID
            1 -> start time
            2 -> end time
            3 -> difference

    sort_ascending
        Set sort direction (boolean; it true then the sort direction is ascending, otherwise descending)
    max_ret_cases
        Set the maximum number of returned cases

    Returns
    -----------
    ret
        Dictionary of cases associated to their start timestamp, their end timestamp and their duration
    """

    statistics_list = []

    for trace in trace_log:
        if trace:
            ci = trace.attributes[case_id_key]
            st = trace[0][timestamp_key].timestamp()
            et = trace[-1][timestamp_key].timestamp()
            diff = et - st
            statistics_list.append([ci, st, et, diff])

    if enable_sort:
        statistics_list = sorted(statistics_list, key=lambda x: x[sort_by_index], reverse=not(sort_ascending))

    if max_ret_cases is not None:
        statistics_list = statistics_list[:max(len(statistics_list), max_ret_cases)]

    statistics_dict = {}

    for el in statistics_list:
        statistics_dict[str(el[0])] = {"startTime": el[1], "endTime": el[2], "caseDuration": el[3]}

    return statistics_dict
from pm4py.objects.dfg.retrieval import log as log_retrieval


def apply(log, activity, parameters=None):
    """
    Gets the time passed from each preceding activity and to each succeeding activity

    Parameters
    -------------
    log
        Log
    activity
        Activity that we are considering
    parameters
        Possible parameters of the algorithm

    Returns
    -------------
    dictio
        Dictionary containing a 'pre' key with the
        list of aggregated times from each preceding activity to the given activity
        and a 'post' key with the list of aggregates times from the given activity
        to each succeeding activity
    """
    if parameters is None:
        parameters = {}

    dfg_frequency = log_retrieval.native(log, parameters=parameters)
    dfg_performance = log_retrieval.performance(log, parameters=parameters)

    pre = []
    sum_perf_post = 0.0
    sum_acti_post = 0.0
    post = []
    sum_perf_pre = 0.0
    sum_acti_pre = 0.0

    for entry in dfg_performance.keys():
        if entry[1] == activity:
            pre.append([entry[0], float(dfg_performance[entry]), int(dfg_frequency[entry])])
            sum_perf_pre = sum_perf_pre + float(dfg_performance[entry]) * float(dfg_frequency[entry])
            sum_acti_pre = sum_acti_pre + float(dfg_frequency[entry])
        if entry[0] == activity:
            post.append([entry[1], float(dfg_performance[entry]), int(dfg_frequency[entry])])
            sum_perf_post = sum_perf_post + float(dfg_performance[entry]) * float(dfg_frequency[entry])
            sum_acti_post = sum_acti_post + float(dfg_frequency[entry])

    perf_acti_pre = 0.0
    if sum_acti_pre > 0:
        perf_acti_pre = sum_perf_pre / sum_acti_pre
    perf_acti_post = 0.0
    if sum_acti_post > 0:
        perf_acti_post = sum_perf_post / sum_acti_post

    return {"pre": pre, "post": post, "post_avg_perf": perf_acti_post, "pre_avg_perf": perf_acti_pre}

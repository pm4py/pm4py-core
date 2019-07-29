from pm4py.algo.discovery.dfg import factory as dfg_factory


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

    dfg_frequency = dfg_factory.apply(log, variant="frequency", parameters=parameters)
    dfg_performance = dfg_factory.apply(log, variant="performance", parameters=parameters)

    pre = []
    post = []

    for entry in dfg_performance.keys():
        if entry[1] == activity:
            pre.append([entry[0], float(dfg_performance[entry]), int(dfg_frequency[entry])])
        if entry[0] == activity:
            post.append([entry[1], float(dfg_performance[entry]), int(dfg_frequency[entry])])

    return {"pre": pre, "post": post}

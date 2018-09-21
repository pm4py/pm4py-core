from pm4py.algo.discovery.dfg.utils.dfg_utils import get_max_activity_count, get_activities_from_dfg

def clean_dfg_based_on_noise_thresh(dfg, activities, noiseThreshold):
    """
    Clean Directly-Follows graph based on noise threshold
    when a fallback (flower) is chosen

    Parameters
    ----------
    dfg
        Directly-Follows graph
    activities
        Activities in the DFG graph
    noiseThreshold
        Noise threshold

    Returns
    ----------
    newDfg
        Cleaned dfg based on noise threshold
    """

    if activities is None:
        activities = get_activities_from_dfg(dfg)

    newDfg = []
    activ_max_count = {}
    for act in activities:
        activ_max_count[act] = get_max_activity_count(dfg, act)

    for el in dfg:
        act1 = el[0][0]
        act2 = el[0][1]
        val = el[1]

        if val < max(activ_max_count[act1] * noiseThreshold, activ_max_count[act2] * noiseThreshold):
            pass
        else:
            newDfg.append(el)

    return newDfg
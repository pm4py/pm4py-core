from pm4py.algo.discovery.dfg.utils.dfg_utils import get_max_activity_count, get_activities_from_dfg
from pm4py.algo.filtering.common import filtering_constants

def clean_dfg_based_on_noise_thresh(dfg, activities, noiseThreshold):
    """
    Clean Directly-Follows graph based on noise threshold

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

    newDfg = None
    activ_max_count = {}
    for act in activities:
        activ_max_count[act] = get_max_activity_count(dfg, act)

    for el in dfg:
        if type(el[0]) is str:
            if newDfg is None:
                newDfg = {}
            act1 = el[0]
            act2 = el[1]
            val = dfg[el]
        else:
            if newDfg is None:
                newDfg = []
            act1 = el[0][0]
            act2 = el[0][1]
            val = el[1]

        if val < max(activ_max_count[act1] * noiseThreshold, activ_max_count[act2] * noiseThreshold):
            pass
        else:
            if type(el[0]) is str:
                newDfg[el] = dfg[el]
                pass
            else:
                newDfg.append(el)
                pass

    return newDfg


def apply(dfg, parameters=None):
    """
    Clean Directly-Follows graph based on noise threshold

    Parameters
    -----------
    dfg
        Directly-Follows graph
    parameters
        Possible parameters of the algorithm, including:
            noiseThreshold -> Threshold of noise in the algorithm

    Returns
    ----------
    newDfg
        Cleaned dfg based on noise threshold
    """
    if parameters is None:
        parameters = {}
    noiseThreshold = parameters[
        "noiseThreshold"] if "noiseThreshold" in parameters else filtering_constants.DEFAULT_NOISE_THRESH_DF

    return clean_dfg_based_on_noise_thresh(dfg, None, noiseThreshold)
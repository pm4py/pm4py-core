from pm4py.objects.dfg.utils.dfg_utils import get_max_activity_count, get_activities_from_dfg
from pm4py.util import constants

DEFAULT_NOISE_THRESH_DF = 0.16


def clean_dfg_based_on_noise_thresh(dfg, activities, noise_threshold, parameters=None):
    """
    Clean Directly-Follows graph based on noise threshold

    Parameters
    ----------
    dfg
        Directly-Follows graph
    activities
        Activities in the DFG graph
    noise_threshold
        Noise threshold

    Returns
    ----------
    newDfg
        Cleaned dfg based on noise threshold
    """
    if parameters is None:
        parameters = {}

    most_common_paths = parameters[
        constants.PARAM_MOST_COMMON_PATHS] if constants.PARAM_MOST_COMMON_PATHS in parameters else None
    if most_common_paths is None:
        most_common_paths = []

    new_dfg = None
    activ_max_count = {}
    for act in activities:
        activ_max_count[act] = get_max_activity_count(dfg, act)

    for el in dfg:
        if type(el[0]) is str:
            if new_dfg is None:
                new_dfg = {}
            act1 = el[0]
            act2 = el[1]
            val = dfg[el]
        else:
            if new_dfg is None:
                new_dfg = []
            act1 = el[0][0]
            act2 = el[0][1]
            val = el[1]

        if not el in most_common_paths and val < min(activ_max_count[act1] * noise_threshold,
                                                     activ_max_count[act2] * noise_threshold):
            pass
        else:
            if type(el[0]) is str:
                new_dfg[el] = dfg[el]
                pass
            else:
                new_dfg.append(el)
                pass

    if new_dfg is None:
        return dfg

    return new_dfg


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
    noise_threshold = parameters[
        "noiseThreshold"] if "noiseThreshold" in parameters else DEFAULT_NOISE_THRESH_DF

    activities = get_activities_from_dfg(dfg)

    return clean_dfg_based_on_noise_thresh(dfg, activities, noise_threshold)

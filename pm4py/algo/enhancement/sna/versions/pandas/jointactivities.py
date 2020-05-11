from collections import Counter

import numpy as np

from pm4py.util import xes_constants as xes
from pm4py.util import exec_utils
from pm4py.algo.enhancement.sna.parameters import Parameters


def apply(log, parameters=None):
    """
    Calculates the Joint Activities / Similar Task metric

    Parameters
    ------------
    log
        Log
    parameters
        Possible parameters of the algorithm

    Returns
    -----------
    tuple
        Tuple containing the metric matrix and the resources list. Moreover, last boolean indicates that the metric is
        directed.
    """
    from scipy.stats import pearsonr

    if parameters is None:
        parameters = {}

    resource_key = exec_utils.get_param_value(Parameters.RESOURCE_KEY, parameters, xes.DEFAULT_RESOURCE_KEY)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes.DEFAULT_NAME_KEY)

    activities = dict(log[activity_key].value_counts())
    resources = dict(log[resource_key].value_counts())
    activity_resource_couples = dict(log.groupby([resource_key, activity_key]).size())
    activities_keys = sorted(list(activities.keys()))
    resources_keys = sorted(list(resources.keys()))
    rsc_act_matrix = np.zeros((len(resources_keys), len(activities_keys)))
    for arc in activity_resource_couples.keys():
        i = resources_keys.index(arc[0])
        j = activities_keys.index(arc[1])
        rsc_act_matrix[i, j] += activity_resource_couples[arc]
    metric_matrix = np.zeros((len(resources_keys), len(resources_keys)))
    for i in range(rsc_act_matrix.shape[0]):
        vect_i = rsc_act_matrix[i, :]
        for j in range(rsc_act_matrix.shape[0]):
            if not i == j:
                vect_j = rsc_act_matrix[j, :]
                r, p = pearsonr(vect_i, vect_j)
                metric_matrix[i, j] = r
    return [metric_matrix, resources_keys, False]

from collections import Counter

import numpy as np
from scipy.stats import pearsonr

from pm4py.objects.conversion.log import factory as conv_factory
from pm4py.objects.log.util import xes
from pm4py.util import constants


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
    if parameters is None:
        parameters = {}

    resource_key = parameters[
        constants.PARAMETER_CONSTANT_RESOURCE_KEY] if constants.PARAMETER_CONSTANT_RESOURCE_KEY in parameters else xes.DEFAULT_RESOURCE_KEY
    activity_key = parameters[
        constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY
    stream = conv_factory.apply(log, variant=conv_factory.TO_EVENT_STREAM)
    activities = Counter(event[activity_key] for event in stream)
    resources = Counter(event[resource_key] for event in stream)
    activity_resource_couples = Counter((event[resource_key], event[activity_key]) for event in stream)
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
    return (metric_matrix, resources_keys, False)

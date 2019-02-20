import numpy

from pm4py.algo.filtering.log.variants import variants_filter
from pm4py.objects.log.util import xes
from pm4py.util import constants

N = "n"


def apply(log, parameters=None):
    """
    Calculates the Subcontracting metric

    Parameters
    ------------
    log
        Log
    parameters
        Possible parameters of the algorithm:
            n -> n of the algorithm proposed in the Wil SNA paper

    Returns
    -----------
    tuple
        Tuple containing the metric matrix and the resources list
    """
    if parameters is None:
        parameters = {}

    resource_key = parameters[
        constants.PARAMETER_CONSTANT_RESOURCE_KEY] if constants.PARAMETER_CONSTANT_RESOURCE_KEY in parameters else xes.DEFAULT_RESOURCE_KEY
    n = parameters[N] if N in parameters else 2

    parameters_variants = {constants.PARAMETER_CONSTANT_ACTIVITY_KEY: resource_key,
                           constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY: resource_key}
    variants_occ = {x: len(y) for x, y in variants_filter.get_variants(log, parameters=parameters_variants).items()}
    variants_resources = list(variants_occ.keys())
    resources = [x.split(",") for x in variants_resources]
    flat_list = sorted(list(set([item for sublist in resources for item in sublist])))

    metric_matrix = numpy.zeros((len(flat_list), len(flat_list)))

    sum_i_to_j = {}

    for rv in resources:
        for i in range(len(rv) - n):
            res_i = flat_list.index(rv[i])
            res_i_n = flat_list.index(rv[i + n])
            if res_i == res_i_n:
                if res_i not in sum_i_to_j:
                    sum_i_to_j[res_i] = {}
                    for j in range(i + 1, i + n):
                        res_j = flat_list.index(rv[j])
                        if res_j not in sum_i_to_j[res_i]:
                            sum_i_to_j[res_i][res_j] = 0
                        sum_i_to_j[res_i][res_j] += variants_occ[",".join(rv)]

    dividend = 0
    for rv in resources:
        dividend = dividend + variants_occ[",".join(rv)] * (len(rv) - 1)

    for key1 in sum_i_to_j:
        for key2 in sum_i_to_j[key1]:
            metric_matrix[key1][key2] = sum_i_to_j[key1][key2] / dividend

    return (metric_matrix, flat_list, True)

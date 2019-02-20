import numpy

from pm4py.objects.log.util import xes
from pm4py.statistics.traces.pandas.case_statistics import get_variant_statistics
from pm4py.util import constants

BETA = "beta"


def apply(log, parameters=None):
    """
    Calculates the HW metric

    Parameters
    ------------
    log
        Log
    parameters
        Possible parameters of the algorithm:
            beta -> beta value as described in the Wil SNA paper

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
    beta = parameters[BETA] if BETA in parameters else 0

    parameters_variants = {constants.PARAMETER_CONSTANT_ACTIVITY_KEY: resource_key,
                           constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY: resource_key}

    variants_occ = {x["variant"]: x["case:concept:name"] for x in
                    get_variant_statistics(log, parameters=parameters_variants)}
    variants_resources = list(variants_occ.keys())
    resources = [x.split(",") for x in variants_resources]
    flat_list = sorted(list(set([item for sublist in resources for item in sublist])))

    metric_matrix = numpy.zeros((len(flat_list), len(flat_list)))

    sum_i_to_j = {}

    for rv in resources:
        for i in range(len(rv) - 1):
            res_i = flat_list.index(rv[i])
            if not res_i in sum_i_to_j:
                sum_i_to_j[res_i] = {}
            for j in range(i + 1, len(rv)):
                res_j = flat_list.index(rv[j])
                if not res_j in sum_i_to_j[res_i]:
                    sum_i_to_j[res_i][res_j] = 0
                if beta == 0:
                    sum_i_to_j[res_i][res_j] += variants_occ[",".join(rv)]
                    break
                else:
                    sum_i_to_j[res_i][res_j] += variants_occ[",".join(rv)] * (beta ** (j - i - 1))

    dividend = 0
    for rv in resources:
        if beta == 0:
            dividend = dividend + variants_occ[",".join(rv)] * (len(rv) - 1)
        else:
            dividend = dividend + variants_occ[",".join(rv)] * (len(rv) - 1)

    for key1 in sum_i_to_j:
        for key2 in sum_i_to_j[key1]:
            metric_matrix[key1][key2] = sum_i_to_j[key1][key2] / dividend

    return (metric_matrix, flat_list, True)

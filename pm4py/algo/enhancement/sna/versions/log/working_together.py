import numpy

from pm4py.algo.filtering.log.variants import variants_filter
from pm4py.objects.log.util import xes
from pm4py.util import constants


def apply(log, parameters=None):
    """
    Calculates the Working Together metric

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
        not directed.
    """

    if parameters is None:
        parameters = {}

    resource_key = parameters[
        constants.PARAMETER_CONSTANT_RESOURCE_KEY] if constants.PARAMETER_CONSTANT_RESOURCE_KEY in parameters else xes.DEFAULT_RESOURCE_KEY

    parameters_variants = {constants.PARAMETER_CONSTANT_ACTIVITY_KEY: resource_key,
                           constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY: resource_key}
    variants_occ = {x: len(y) for x, y in variants_filter.get_variants(log, parameters=parameters_variants).items()}
    variants_resources = list(variants_occ.keys())
    resources = [x.split(",") for x in variants_resources]
    flat_list = sorted(list(set([item for sublist in resources for item in sublist])))

    metric_matrix = numpy.zeros((len(flat_list), len(flat_list)))

    for rv in resources:
        ord_res_list = sorted(list(set(rv)))

        for i in range(len(ord_res_list) - 1):
            res_i = flat_list.index(ord_res_list[i])
            for j in range(i + 1, len(ord_res_list)):
                res_j = flat_list.index(ord_res_list[j])
                metric_matrix[res_i, res_j] += float(variants_occ[",".join(rv)]) / float(len(log))
                metric_matrix[res_j, res_i] += float(variants_occ[",".join(rv)]) / float(len(log))

    return (metric_matrix, flat_list, False)

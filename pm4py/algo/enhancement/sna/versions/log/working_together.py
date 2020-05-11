import numpy

from pm4py.statistics.variants.log import get as variants_filter
from pm4py.util import xes_constants as xes
from pm4py.util import exec_utils
from pm4py.algo.enhancement.sna.parameters import Parameters


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

    resource_key = exec_utils.get_param_value(Parameters.RESOURCE_KEY, parameters, xes.DEFAULT_RESOURCE_KEY)

    parameters_variants = {variants_filter.Parameters.ACTIVITY_KEY: resource_key,
                           variants_filter.Parameters.ATTRIBUTE_KEY: resource_key}
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

    return [metric_matrix, flat_list, False]

'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
import numpy

from pm4py.statistics.variants.log import get as variants_filter
from pm4py.util import xes_constants as xes
from enum import Enum
from pm4py.util import constants, exec_utils
from pm4py.util import variants_util


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    RESOURCE_KEY = constants.PARAMETER_CONSTANT_RESOURCE_KEY
    N = "n"


N = Parameters.N


def apply(log, parameters=None):
    """
    Calculates the Subcontracting metric

    Parameters
    ------------
    log
        Log
    parameters
        Possible parameters of the algorithm:
            Parameters.N -> n of the algorithm proposed in the Wil SNA paper

    Returns
    -----------
    tuple
        Tuple containing the metric matrix and the resources list
    """
    if parameters is None:
        parameters = {}

    resource_key = exec_utils.get_param_value(Parameters.RESOURCE_KEY, parameters, xes.DEFAULT_RESOURCE_KEY)
    n = exec_utils.get_param_value(Parameters.N, parameters, 2)

    parameters_variants = {variants_filter.Parameters.ACTIVITY_KEY: resource_key,
                           variants_filter.Parameters.ATTRIBUTE_KEY: resource_key}
    variants_occ = {x: len(y) for x, y in variants_filter.get_variants(log, parameters=parameters_variants).items()}
    variants_resources = list(variants_occ.keys())
    resources = [variants_util.get_activities_from_variant(y) for y in variants_resources]

    flat_list = sorted(list(set([item for sublist in resources for item in sublist])))

    metric_matrix = numpy.zeros((len(flat_list), len(flat_list)))

    sum_i_to_j = {}

    for idx, rv in enumerate(resources):
        rvj = variants_resources[idx]

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
                        sum_i_to_j[res_i][res_j] += variants_occ[rvj]

    dividend = 0
    for idx, rv in enumerate(resources):
        rvj = variants_resources[idx]
        dividend = dividend + variants_occ[rvj] * (len(rv) - 1)

    for key1 in sum_i_to_j:
        for key2 in sum_i_to_j[key1]:
            metric_matrix[key1][key2] = sum_i_to_j[key1][key2] / dividend

    return [metric_matrix, flat_list, True]

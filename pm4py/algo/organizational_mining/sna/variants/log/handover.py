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

from typing import Optional, Dict, Any, Union
from pm4py.objects.log.obj import EventLog
from pm4py.objects.org.sna.obj import SNA


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    RESOURCE_KEY = constants.PARAMETER_CONSTANT_RESOURCE_KEY
    BETA = "beta"


BETA = Parameters.BETA


def apply(log: EventLog, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> SNA:
    """
    Calculates the HW metric

    Parameters
    ------------
    log
        Log
    parameters
        Possible parameters of the algorithm:
            Parameters.BETA -> beta value as described in the Wil SNA paper

    Returns
    -----------
    tuple
        Tuple containing the metric matrix and the resources list. Moreover, last boolean indicates that the metric is
        directed.
    """
    if parameters is None:
        parameters = {}

    resource_key = exec_utils.get_param_value(Parameters.RESOURCE_KEY, parameters, xes.DEFAULT_RESOURCE_KEY)
    beta = exec_utils.get_param_value(Parameters.BETA, parameters, 0)

    parameters_variants = {variants_filter.Parameters.ACTIVITY_KEY: resource_key,
                           variants_filter.Parameters.ATTRIBUTE_KEY: resource_key}
    variants_occ = {x: len(y) for x, y in variants_filter.get_variants(log, parameters=parameters_variants).items()}
    variants_resources = list(variants_occ.keys())
    resources = [variants_util.get_activities_from_variant(y) for y in variants_resources]

    flat_list = sorted(list(set([item for sublist in resources for item in sublist])))

    metric_matrix = numpy.zeros((len(flat_list), len(flat_list)))

    sum_i_to_j = {}
    dividend = 0

    for idx, rv in enumerate(resources):
        rvj = variants_resources[idx]
        for i in range(len(rv) - 1):
            res_i = flat_list.index(rv[i])
            if not res_i in sum_i_to_j:
                sum_i_to_j[res_i] = {}
            for j in range(i + 1, len(rv)):
                res_j = flat_list.index(rv[j])
                if not res_j in sum_i_to_j[res_i]:
                    sum_i_to_j[res_i][res_j] = 0
                if beta == 0:
                    sum_i_to_j[res_i][res_j] += variants_occ[rvj]
                    dividend += variants_occ[rvj]
                    break
                else:
                    sum_i_to_j[res_i][res_j] += variants_occ[rvj] * (beta ** (j - i - 1))
                    dividend += variants_occ[rvj] * (beta ** (j - i - 1))

    connections = {}
    for key1 in sum_i_to_j:
        for key2 in sum_i_to_j[key1]:
            connections[(flat_list[key1], flat_list[key2])] = sum_i_to_j[key1][key2] / dividend

    return SNA(connections, True)


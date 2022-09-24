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
from pm4py.statistics.variants.log import get as variants_filter
from pm4py.util import xes_constants as xes
from pm4py.util import exec_utils
from pm4py.util import variants_util
from enum import Enum
from pm4py.util import constants

from typing import Optional, Dict, Any, Union
from pm4py.objects.log.obj import EventLog
from pm4py.objects.org.sna.obj import SNA
from collections import Counter


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    RESOURCE_KEY = constants.PARAMETER_CONSTANT_RESOURCE_KEY
    METRIC_NORMALIZATION = "metric_normalization"


def apply(log: EventLog, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> SNA:
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
    resources = [variants_util.get_activities_from_variant(y) for y in variants_resources]

    flat_list = sorted(list(set([item for sublist in resources for item in sublist])))

    connections = Counter()

    for idx, rv in enumerate(resources):
        rvj = variants_resources[idx]

        ord_res_list = sorted(list(set(rv)))

        for i in range(len(ord_res_list) - 1):
            res_i = flat_list.index(ord_res_list[i])
            for j in range(i + 1, len(ord_res_list)):
                res_j = flat_list.index(ord_res_list[j])
                connections[(flat_list[res_i], flat_list[res_j])] += float(variants_occ[rvj]) / float(len(log))
                connections[(flat_list[res_j], flat_list[res_i])] += float(variants_occ[rvj]) / float(len(log))

    return SNA(dict(connections), False)

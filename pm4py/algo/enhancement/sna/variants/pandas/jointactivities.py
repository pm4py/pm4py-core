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
    import numpy as np
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

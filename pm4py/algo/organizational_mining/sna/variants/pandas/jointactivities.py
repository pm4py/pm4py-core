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
from enum import Enum
from pm4py.util import constants

from typing import Optional, Dict, Any, Union
import pandas as pd
from pm4py.objects.org.sna.obj import SNA


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    RESOURCE_KEY = constants.PARAMETER_CONSTANT_RESOURCE_KEY
    METRIC_NORMALIZATION = "metric_normalization"


def apply(log: pd.DataFrame, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> SNA:
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

    activities = log[activity_key].value_counts().to_dict()
    resources = log[resource_key].value_counts().to_dict()
    activity_resource_couples = log.groupby([resource_key, activity_key]).size().to_dict()
    activities_keys = sorted(list(activities.keys()))
    resources_keys = sorted(list(resources.keys()))
    rsc_act_matrix = np.zeros((len(resources_keys), len(activities_keys)))
    for arc in activity_resource_couples.keys():
        i = resources_keys.index(arc[0])
        j = activities_keys.index(arc[1])
        rsc_act_matrix[i, j] += activity_resource_couples[arc]
    connections = {}
    for i in range(rsc_act_matrix.shape[0]):
        vect_i = rsc_act_matrix[i, :]
        for j in range(rsc_act_matrix.shape[0]):
            if not i == j:
                vect_j = rsc_act_matrix[j, :]
                r, p = pearsonr(vect_i, vect_j)
                connections[(resources_keys[i], resources_keys[j])] = r

    return SNA(connections, False)

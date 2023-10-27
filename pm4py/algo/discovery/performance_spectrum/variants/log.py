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
from pm4py.objects.log.util import sorting
from pm4py.objects.log.util import basic_filter
from pm4py.util import points_subset
from pm4py.util import xes_constants as xes
from pm4py.util import exec_utils
from enum import Enum
from pm4py.util import constants
from typing import Optional, Dict, Any, Union, List
from pm4py.objects.log.obj import EventLog


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    ATTRIBUTE_KEY = constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY
    PARAMETER_SAMPLE_SIZE = "sample_size"
    SORT_LOG_REQUIRED = "sort_log_required"


def apply(log: EventLog, list_activities: List[str], sample_size: int, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Dict[str, Any]:
    """
    Finds the performance spectrum provided a log
    and a list of activities

    Parameters
    -------------
    log
        Log
    list_activities
        List of activities interesting for the performance spectrum (at least two)
    sample_size
        Size of the sample
    parameters
        Parameters of the algorithm,  including:
            - Parameters.ACTIVITY_KEY
            - Parameters.TIMESTAMP_KEY

    Returns
    -------------
    points
        Points of the performance spectrum
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes.DEFAULT_TIMESTAMP_KEY)
    sort_log_required = exec_utils.get_param_value(Parameters.SORT_LOG_REQUIRED, parameters, True)

    parameters[Parameters.ATTRIBUTE_KEY] = activity_key
    log = basic_filter.filter_log_events_attr(log, list_activities, parameters=parameters)
    if sort_log_required:
        log = sorting.sort_timestamp_log(log, timestamp_key=timestamp_key)

    points = []

    for trace in log:
        for i in range(len(trace)-len(list_activities)+1):
            acti_comb = [event[activity_key] for event in trace[i:i+len(list_activities)]]

            if acti_comb == list_activities:
                timest_comb = [event[timestamp_key].timestamp() for event in trace[i:i+len(list_activities)]]

                points.append(timest_comb)

    points = sorted(points, key=lambda x: x[0])

    if len(points) > sample_size:
        points = points_subset.pick_chosen_points_list(sample_size, points)

    return points

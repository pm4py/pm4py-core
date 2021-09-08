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
from enum import Enum
from typing import Optional, Dict, Any, Union

from pm4py.objects.log.obj import EventLog
from pm4py.util import exec_utils, constants, xes_constants


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY


def apply(log: EventLog, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Dict[str, Dict[str, int]]:
    """
    Computes for each trace of the event log how much rework occurs.
    The rework is computed as the difference between the total number of activities of a trace and the
    number of unique activities.

    Parameters
    ----------------
    log
        Event log
    parameters
        Parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY => the activity key
        - Parameters.CASE_ID_KEY => the case identifier attribute

    Returns
    -----------------
    dict
        Dictionary associating to each case ID:
        - The number of total activities of the case (number of events)
        - The rework (difference between the total number of activities of a trace and the number of unique activities)
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, xes_constants.DEFAULT_TRACEID_KEY)

    rework_cases = {}
    for trace in log:
        activities = list([x[activity_key] for x in trace])
        unique_activities = set(activities)
        rework = len(activities) - len(unique_activities)
        rework_cases[trace.attributes[case_id_key]] = {"number_activities": len(activities), "rework": rework}

    return rework_cases

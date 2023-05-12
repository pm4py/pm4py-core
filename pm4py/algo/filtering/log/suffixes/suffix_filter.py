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
from pm4py.util import exec_utils, xes_constants, constants
from pm4py.objects.log.obj import EventLog, EventStream, Trace
from typing import Dict, Optional, Any, Union
from pm4py.objects.conversion.log import converter as log_converter


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    STRICT = "strict"
    FIRST_OR_LAST = "first_or_last"


def apply(log: Union[EventLog, EventStream], activity: str, parameters: Optional[Dict[Any, Any]] = None) -> EventLog:
    """
    Filters the suffixes of an activity in the event log

    Parameters
    ----------------
    log
        Event log
    activity
        Target activity
    parameters
        Parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY => the activity.
        - Parameters.STRICT => applies the filter strictly (cuts the occurrences of the selected activity).
        - Parameters.FIRST_OR_LAST => decides if the first or last occurrence of an activity should be selected.

    Returns
    ----------------
    filtered_log
        Filtered event log
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    first_or_last = exec_utils.get_param_value(Parameters.FIRST_OR_LAST, parameters, "first")
    strict = exec_utils.get_param_value(Parameters.STRICT, parameters, True)

    filtered_log = EventLog(attributes=log.attributes, extensions=log.extensions, globals=log.omni_present,
                       classifiers=log.classifiers, properties=log.properties)

    for trace in log:
        activities = [x[activity_key] if activity_key in x else None for x in trace]
        if activity in activities:
            if first_or_last == "first":
                op = min
            else:
                op = max
            idx_activity = op(i for i in range(len(activities)) if activities[i] == activity)
            if strict:
                idx_activity = idx_activity + 1
            filtered_trace = Trace(attributes=trace.attributes, properties=trace.properties)
            for i in range(idx_activity, len(trace)):
                filtered_trace.append(trace[i])
            filtered_log.append(filtered_trace)

    return filtered_log

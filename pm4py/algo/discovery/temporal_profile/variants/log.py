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
from statistics import mean, stdev
from typing import Optional, Dict, Any

from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.obj import EventLog
from pm4py.util import exec_utils, constants, xes_constants
from pm4py.util import typing
from pm4py.util.business_hours import BusinessHours


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    BUSINESS_HOURS = "business_hours"
    WORKTIMING = "worktiming"
    WEEKENDS = "weekends"


def apply(log: EventLog, parameters: Optional[Dict[Any, Any]] = None) -> typing.TemporalProfile:
    """
    Gets the temporal profile from the log.

    Implements the approach described in:
    Stertz, Florian, Jürgen Mangler, and Stefanie Rinderle-Ma. "Temporal Conformance Checking at Runtime based on Time-infused Process Models." arXiv preprint arXiv:2008.07262 (2020).


    Parameters
    ----------
    log
        Event log
    parameters
        Parameters, including:
        - Parameters.ACTIVITY_KEY => the attribute to use as activity
        - Parameters.START_TIMESTAMP_KEY => the attribute to use as start timestamp
        - Parameters.TIMESTAMP_KEY => the attribute to use as timestamp
        - Parameters.BUSINESS_HOURS => calculates the difference of time based on the business hours, not the total time.
                                        Default: False
        - Parameters.WORKTIMING => work schedule of the company (provided as a list where the first number is the start
            of the work time, and the second number is the end of the work time), if business hours are enabled
                                        Default: [7, 17] (work shift from 07:00 to 17:00)
        - Parameters.WEEKENDS => indexes of the days of the week that are weekend
                                        Default: [6, 7] (weekends are Saturday and Sunday)

    Returns
    -------
    temporal_profile
        Temporal profile of the log
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, parameters=parameters)

    business_hours = exec_utils.get_param_value(Parameters.BUSINESS_HOURS, parameters, False)
    worktiming = exec_utils.get_param_value(Parameters.WORKTIMING, parameters, [7, 17])
    weekends = exec_utils.get_param_value(Parameters.WEEKENDS, parameters, [6, 7])

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters,
                                                     xes_constants.DEFAULT_TIMESTAMP_KEY)

    diff_time_recordings = {}

    for trace in log:
        for i in range(len(trace) - 1):
            act_i = trace[i][activity_key]
            time_i = trace[i][timestamp_key].timestamp()
            for j in range(i + 1, len(trace)):
                time_j = trace[j][start_timestamp_key].timestamp()
                if time_j >= time_i:
                    act_j = trace[j][activity_key]
                    if not (act_i, act_j) in diff_time_recordings:
                        diff_time_recordings[(act_i, act_j)] = []
                    if business_hours:
                        bh = BusinessHours(trace[i][timestamp_key].replace(tzinfo=None),
                                           trace[j][start_timestamp_key].replace(tzinfo=None),
                                           worktiming=worktiming,
                                           weekends=weekends)
                        diff_time_recordings[(act_i, act_j)].append(bh.getseconds())
                    else:
                        diff_time_recordings[(act_i, act_j)].append(time_j - time_i)

    temporal_profile = {}
    for ac in diff_time_recordings:
        if len(diff_time_recordings[ac]) > 1:
            temporal_profile[ac] = (mean(diff_time_recordings[ac]), stdev(diff_time_recordings[ac]))
        else:
            temporal_profile[ac] = (diff_time_recordings[ac][0], 0)

    return temporal_profile

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
from pm4py.util.xes_constants import DEFAULT_TIMESTAMP_KEY
import statistics
from pm4py.util.business_hours import BusinessHours
from pm4py.util import exec_utils, constants
from enum import Enum
from typing import Optional, Dict, Any, Union
from pm4py.objects.log.obj import EventLog
from pm4py.objects.conversion.log import converter as log_converter


class Parameters(Enum):
    ATTRIBUTE_KEY = constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY

    BUSINESS_HOURS = "business_hours"
    BUSINESS_HOUR_SLOTS = "business_hour_slots"
    WORKCALENDAR = "workcalendar"


def get_case_arrival_avg(log: EventLog, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> float:
    """
    Gets the average time interlapsed between case starts

    Parameters
    --------------
    log
        Trace log
    parameters
        Parameters of the algorithm, including:
            Parameters.TIMESTAMP_KEY -> attribute of the log to be used as timestamp

    Returns
    --------------
    case_arrival_avg
        Average time interlapsed between case starts
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    business_hours = exec_utils.get_param_value(Parameters.BUSINESS_HOURS, parameters, False)
    business_hours_slots = exec_utils.get_param_value(Parameters.BUSINESS_HOUR_SLOTS, parameters, constants.DEFAULT_BUSINESS_HOUR_SLOTS)
    workcalendar = exec_utils.get_param_value(Parameters.WORKCALENDAR, parameters, constants.DEFAULT_BUSINESS_HOURS_WORKCALENDAR)

    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY)

    case_start_time = [trace[0][timestamp_key] for trace in log if trace and timestamp_key in trace[0]]
    case_start_time = sorted(case_start_time)

    case_diff_start_time = []
    for i in range(len(case_start_time)-1):
        if business_hours:
            bh = BusinessHours(case_start_time[i], case_start_time[i+1],
                               business_hour_slots=business_hours_slots, workcalendar=workcalendar)
            case_diff_start_time.append(bh.get_seconds())
        else:
            case_diff_start_time.append((case_start_time[i+1]-case_start_time[i]).total_seconds())

    if case_diff_start_time:
        return statistics.mean(case_diff_start_time)

    return 0.0


def get_case_dispersion_avg(log: EventLog, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> float:
    """
    Gets the average time interlapsed between case ends

    Parameters
    --------------
    log
        Trace log
    parameters
        Parameters of the algorithm, including:
            Parameters.TIMESTAMP_KEY -> attribute of the log to be used as timestamp

    Returns
    --------------
    case_dispersion_avg
        Average time interlapsed between the completion of cases
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    business_hours = exec_utils.get_param_value(Parameters.BUSINESS_HOURS, parameters, False)
    business_hours_slots = exec_utils.get_param_value(Parameters.BUSINESS_HOUR_SLOTS, parameters, constants.DEFAULT_BUSINESS_HOUR_SLOTS)

    workcalendar = exec_utils.get_param_value(Parameters.WORKCALENDAR, parameters, constants.DEFAULT_BUSINESS_HOURS_WORKCALENDAR)

    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY)

    case_end_time = [trace[-1][timestamp_key] for trace in log if trace and timestamp_key in trace[0]]
    case_end_time = sorted(case_end_time)

    case_diff_end_time = []
    for i in range(len(case_end_time)-1):
        if business_hours:
            bh = BusinessHours(case_end_time[i], case_end_time[i+1],
                               business_hour_slots=business_hours_slots, workcalendar=workcalendar)
            case_diff_end_time.append(bh.get_seconds())
        else:
            case_diff_end_time.append((case_end_time[i+1]-case_end_time[i]).total_seconds())

    if case_diff_end_time:
        return statistics.mean(case_diff_end_time)

    return 0.0

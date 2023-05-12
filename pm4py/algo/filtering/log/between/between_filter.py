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

from pm4py.objects.log.obj import EventLog, Trace
from pm4py.util import exec_utils, constants, xes_constants
from pm4py.objects.conversion.log import converter as log_converter


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY


def apply(log: EventLog, act1: str, act2: str, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> EventLog:
    """
    Given an event log, filters all the subtraces going from an event with activity "act1" to an event with
    activity "act2"

    Parameters
    ----------------
    log
        Event log
    act1
        First activity
    act2
        Second activity
    parameters
        Parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY => activity key

    Returns
    ----------------
    filtered_log
        Log with all the subtraces going from "act1" to "act2"
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)

    filtered_log = EventLog(attributes=log.attributes, extensions=log.extensions, omni_present=log.omni_present,
                            classifiers=log.classifiers, properties=log.properties)

    for trace in log:
        act1_encountered = False
        filt_trace = None

        i = 0
        while i < len(trace):
            if not act1_encountered and trace[i][activity_key] == act1:
                act1_encountered = True
                filt_trace = Trace(attributes=trace.attributes)
                filt_trace.append(trace[i])
            elif act1_encountered and trace[i][activity_key] == act2:
                filt_trace.append(trace[i])
                filtered_log.append(filt_trace)
                act1_encountered = False
                filt_trace = None
            elif filt_trace is not None:
                filt_trace.append(trace[i])

            i = i + 1

    return filtered_log

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
from typing import Optional, Dict, Any

from pm4py.objects.log.obj import Event
from pm4py.objects.log.obj import EventLog
from pm4py.util import constants
from pm4py.util import exec_utils
from pm4py.util import xes_constants
import datetime


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    PARAM_ARTIFICIAL_START_ACTIVITY = constants.PARAM_ARTIFICIAL_START_ACTIVITY
    PARAM_ARTIFICIAL_END_ACTIVITY = constants.PARAM_ARTIFICIAL_END_ACTIVITY


def insert_artificial_start_end(log: EventLog, parameters: Optional[Dict[Any, Any]] = None) -> EventLog:
    """
    Inserts the artificial start/end activities in an event log

    Parameters
    -------------------
    log
        Event log
     parameters
        Parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY: the activity
        - Parameters.TIMESTAMP_KEY: the timestamp

    Returns
    ------------------
    log
        Enriched log
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)

    artificial_start_activity = exec_utils.get_param_value(Parameters.PARAM_ARTIFICIAL_START_ACTIVITY, parameters,
                                                           constants.DEFAULT_ARTIFICIAL_START_ACTIVITY)
    artificial_end_activity = exec_utils.get_param_value(Parameters.PARAM_ARTIFICIAL_END_ACTIVITY, parameters,
                                                         constants.DEFAULT_ARTIFICIAL_END_ACTIVITY)

    for trace in log:
        start_event = Event({activity_key: artificial_start_activity})
        end_event = Event({activity_key: artificial_end_activity})
        if trace:
            if timestamp_key in trace[0]:
                start_event[timestamp_key] = trace[0][timestamp_key] - datetime.timedelta(seconds=1)
            if timestamp_key in trace[-1]:
                end_event[timestamp_key] = trace[-1][timestamp_key] + datetime.timedelta(seconds=1)
        trace.insert(0, start_event)
        trace.append(end_event)

    return log

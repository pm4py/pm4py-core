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

from intervaltree import IntervalTree, Interval

from pm4py.objects.log.obj import EventLog
from pm4py.util import exec_utils, constants, xes_constants


class Parameters(Enum):
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    EPSILON = "epsilon"


def apply(log: EventLog, parameters: Optional[Dict[Any, Any]] = None) -> IntervalTree:
    """
    Transforms the event log to an interval tree in which the intervals are the
    directly-follows paths in the log (open at the complete timestamp of the source event,
    and closed at the start timestamp of the target event), and having as associated data the source and the target
    event.

    Parameters
    -----------------
    log
        Event log
    parameters
        Parameters of the algorithm, including:
        - Parameters.START_TIMESTAMP_KEY => the attribute to be used as start timestamp (default: xes_constants.DEFAULT_TIMESTAMP_KEY)
        - Parameters.TIMESTAMP_KEY => the attribute to be used as completion timestamp (default: xes_constants.DEFAULT_TIMESTAMP_KEY)
        - Parameters.EPSILON => the small gap that is removed from the timestamp of the source event and added to the
            timestamp of the target event to make interval querying possible

    Returns
    -----------------
    tree
        Interval tree object (which can be queried at a given timestamp, or range of timestamps)
    """
    if parameters is None:
        parameters = {}

    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters,
                                                     xes_constants.DEFAULT_TIMESTAMP_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    epsilon = exec_utils.get_param_value(Parameters.EPSILON, parameters, 0.00001)

    tree = IntervalTree()

    for trace in log:
        for i in range(len(trace) - 1):
            time_i = trace[i][timestamp_key].timestamp()
            for j in range(i + 1, len(trace)):
                time_j = trace[j][start_timestamp_key].timestamp()
                if time_j >= time_i:
                    #print(time_i, time_j, (time_i + time_j)/2.0)
                    tree.add(Interval(time_i - epsilon, time_j + epsilon,
                                      data={"source_event": trace[i], "target_event": trace[j]}))
                    break

    return tree

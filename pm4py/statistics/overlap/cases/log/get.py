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
from typing import Dict, Optional, Any, List, Union

from pm4py.objects.log.obj import EventLog
from pm4py.statistics.overlap.utils import compute
from pm4py.util import exec_utils, constants, xes_constants
from pm4py.objects.conversion.log import converter


class Parameters(Enum):
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY


def apply(log: EventLog, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> List[int]:
    """
    Computes the case overlap statistic from an interval event log

    Parameters
    -----------------
    log
        Interval event log
    parameters
        Parameters of the algorithm, including:
        - Parameters.TIMESTAMP_KEY => attribute representing the completion timestamp
        - Parameters.START_TIMESTAMP_KEY => attribute representing the start timestamp

    Returns
    ----------------
    case overlap
        List associating to each case the number of open cases during the life of a case
    """
    if parameters is None:
        parameters = {}

    log = converter.apply(log, variant=converter.Variants.TO_EVENT_LOG, parameters=parameters)

    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters,
                                                     xes_constants.DEFAULT_TIMESTAMP_KEY)

    points = []
    for trace in log:
        case_points = []
        for event in trace:
            case_points.append((event[start_timestamp_key].timestamp(), event[timestamp_key].timestamp()))
        points.append((min(x[0] for x in case_points), max(x[1] for x in case_points)))

    return compute.apply(points, parameters=parameters)

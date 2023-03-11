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
from pm4py.util import exec_utils, constants, xes_constants
from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd
from typing import Union, Dict, Optional, Any, Tuple, List
from pm4py.objects.conversion.log import converter as log_converter


class Parameters(Enum):
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY


def apply(log: Union[EventLog, EventStream, pd.DataFrame], parameters: Optional[Dict[Any, Any]] = None) -> Tuple[List[List[int]], List[str]]:
    """
    Returns a list of lists (one for every case of the log) containing the remaining time in seconds
    from an event to the end of the case.

    Parameters
    ---------------
    log
        Event log
    parameters
        Parameters of the algorithm, including:
        - Parameters.TIMESTAMP_KEY => the attribute of the log to be used as timestamp

    Returns
    ---------------
    target
        The aforementioned list
    classes
        Dummy list (of classes)
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)

    target = []
    for trace in log:
        target.append([])
        for i in range(len(trace)):
            curr_time = trace[i][timestamp_key].timestamp()
            last_time = trace[-1][timestamp_key].timestamp()

            target[-1].append(last_time-curr_time)

    return target, ["@@remaining_time"]

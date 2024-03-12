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
    ACTIVITIES = "activities"
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    ENABLE_PADDING = "enable_padding"
    PAD_SIZE = "pad_size"


def apply(log: Union[EventLog, EventStream, pd.DataFrame], parameters: Optional[Dict[Any, Any]] = None) -> Tuple[List[List[List[int]]], List[str]]:
    """
    Returns a list of matrixes (one for every case).
    Every matrix contains as many rows as many events are contained in the case (an automatic padding option is also available),
    and as many columns as many distinct activities are in the log.

    The corresponding activity to the given event is assigned to the value 1;
    the remaining activities are assigned to the value 0.

    Parameters
    --------------
    log
        Event log / Event stream / Pandas dataframe
    parameters
        Parameters of the algorithm, including:
        - Parameters.ACTIVITIES => list of activities to consider
        - Parameters.ACTIVITY_KEY => attribute that should be used as activity
        - Parameters.ENABLE_PADDING => enables the padding (the length of cases is normalized)
        - Parameters.PAD_SIZE => the size of the padding

    Returns
    -------------
    target
        The aforementioned list of matrixes.
    activities
        The considered list of activities
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)
    max_case_length = max([len(x) for x in log])

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    activities = exec_utils.get_param_value(Parameters.ACTIVITIES, parameters, sorted(list(set(y[activity_key] for x in log for y in x))))
    enable_padding = exec_utils.get_param_value(Parameters.ENABLE_PADDING, parameters, False)
    pad_size = exec_utils.get_param_value(Parameters.PAD_SIZE, parameters, max_case_length)

    target = []
    for trace in log:
        target.append([])
        for i in range(len(trace)):
            target[-1].append([0.0] * len(activities))
            if i < len(trace) - 1:
                act = trace[i+1][activity_key]
                if act in activities:
                    target[-1][-1][activities.index(act)] = 1.0
        if enable_padding:
            while len(target[-1]) < pad_size:
                target[-1].append([0.0] * len(activities))

    return target, activities

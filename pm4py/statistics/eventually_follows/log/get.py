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

from pm4py.objects.conversion.log import converter
from pm4py.objects.log.util import sorting
from pm4py.util import exec_utils, constants, xes_constants
from typing import Optional, Dict, Any, Union, Tuple
from pm4py.objects.log.obj import EventLog


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    KEEP_FIRST_FOLLOWING = "keep_first_following"


def apply(interval_log: EventLog, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Dict[Tuple[str, str], int]:
    if parameters is None:
        parameters = {}

    interval_log = converter.apply(interval_log, variant=converter.Variants.TO_EVENT_LOG, parameters=parameters)

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters,
                                                     xes_constants.DEFAULT_TIMESTAMP_KEY)
    keep_first_following = exec_utils.get_param_value(Parameters.KEEP_FIRST_FOLLOWING, parameters, False)

    ret_dict = {}
    for trace in interval_log:
        sorted_trace = sorting.sort_timestamp_trace(trace, start_timestamp_key)
        i = 0
        while i < len(sorted_trace):
            act1 = sorted_trace[i][activity_key]
            tc1 = sorted_trace[i][timestamp_key]
            j = i + 1
            while j < len(sorted_trace):
                ts2 = sorted_trace[j][start_timestamp_key]
                act2 = sorted_trace[j][activity_key]
                if tc1 <= ts2:
                    tup = (act1, act2)
                    if tup not in ret_dict:
                        ret_dict[tup] = 0
                    ret_dict[tup] = ret_dict[tup] + 1
                    if keep_first_following:
                        break
                j = j + 1
            i = i + 1

    return ret_dict

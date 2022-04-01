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
from pm4py.util import constants, xes_constants, exec_utils
from enum import Enum
from collections import Counter
from pm4py.objects.log.obj import EventLog, EventStream
from typing import Union, Optional, Dict, Any
from pm4py.objects.conversion.log import converter as log_converter


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY


def apply(log: Union[EventLog, EventStream], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Dict[str, int]:
    """
    Associates to each activity (with at least one rework) the number of cases in the log for which
    the rework happened.

    Parameters
    ------------------
    log
        Event log
    parameters
        Parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY => the attribute to be used as activity

    Returns
    ------------------
    dict
        Dictionary associating to each activity the number of cases for which the rework happened
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG)

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    ret = Counter()

    for trace in log:
        activities = Counter([x[activity_key] for x in trace])
        activities = [x for x in activities if activities[x] > 1]
        for act in activities:
            ret[act] += 1

    return dict(ret)

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
from pm4py.objects.log.obj import EventLog, XESExtension
from typing import Optional, Dict, Any, Union
from enum import Enum
from pm4py.util import exec_utils
from copy import deepcopy


class Parameters(Enum):
    ENABLE_DEEPCOPY = "enable_deepcopy"


def apply(log: EventLog, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> EventLog:
    """
    Moves the attributes that are constant for all the events of the trace, and they
    do not belong to a standard extension, to the trace level

    Parameters
    ----------------
    log
        Event log
    parameters
        Parameters of the algorithm, including:
        - Parameters.DEEPCOPY => enables the deepcopy of the event log

    Returns
    ----------------
    log
        Event log, where some attribute has been possibly moved from the event to the trace level
    """
    if parameters is None:
        parameters = {}

    enable_deepcopy = exec_utils.get_param_value(Parameters.ENABLE_DEEPCOPY, parameters, False)
    if enable_deepcopy:
        log = deepcopy(log)

    main_extensions = set()
    for e in XESExtension:
        main_extensions.add(e.value[1])

    candidates = None
    for trace in log:
        values_count = {}
        for eve in trace:
            for attr in eve:
                if attr.split(":")[0] not in main_extensions:
                    if attr not in trace.attributes:
                        if attr not in values_count:
                            values_count[attr] = [eve[attr]]
                        else:
                            values_count[attr].append(eve[attr])
        trace_candidates = set(x for x in values_count if len(values_count[x]) == len(trace) and len(set(values_count[x])) == 1)
        if candidates is not None:
            candidates = trace_candidates.intersection(candidates)
        else:
            candidates = trace_candidates

    for attr in candidates:
        for trace in log:
            trace.attributes[attr] = trace[0][attr]
            for ev in trace:
                del ev[attr]

    return log

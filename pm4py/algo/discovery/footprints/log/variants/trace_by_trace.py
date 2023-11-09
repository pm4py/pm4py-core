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
from pm4py.util import constants
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.objects.conversion.log import converter
from pm4py.util import xes_constants
from pm4py.util import exec_utils
from enum import Enum
from typing import Optional, Dict, Any, Union
from pm4py.objects.log.obj import EventLog


class Outputs(Enum):
    DFG = "dfg"
    SEQUENCE = "sequence"
    PARALLEL = "parallel"
    START_ACTIVITIES = "start_activities"
    END_ACTIVITIES = "end_activities"
    ACTIVITIES = "activities"
    SKIPPABLE = "skippable"
    ACTIVITIES_ALWAYS_HAPPENING = "activities_always_happening"
    MIN_TRACE_LENGTH = "min_trace_length"
    TRACE = "trace"


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY


def apply(log, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Dict[str, Any]:
    """
    Discovers a footprint object from an event log
    (the footprints are returned case-by-case)

    Parameters
    --------------
    log
        Log
    parameters
        Parameters of the algorithm:
            - Parameters.ACTIVITY_KEY

    Returns
    --------------
    footprints_obj
        List of footprints for the cases of the log
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)

    log = converter.apply(log, variant=converter.TO_EVENT_LOG, parameters=parameters)

    ret = []

    for trace in log:
        dfg = dfg_discovery.apply(EventLog([trace]), parameters=parameters)
        parallel = {(x, y) for (x, y) in dfg if (y, x) in dfg}
        sequence = {(x, y) for (x, y) in dfg if not (y, x) in dfg}
        trace = tuple(x[activity_key] for x in trace)
        activities = set(trace)
        if len(trace) > 0:
            start_activities = {trace[0]}
            end_activities = {trace[-1]}
        else:
            start_activities = set()
            end_activities = set()

        ret.append(
            {Outputs.DFG.value: dfg, Outputs.SEQUENCE.value: sequence, Outputs.PARALLEL.value: parallel, Outputs.ACTIVITIES.value: activities,
             Outputs.START_ACTIVITIES.value: start_activities, Outputs.END_ACTIVITIES.value: end_activities,
             Outputs.MIN_TRACE_LENGTH.value: len(trace), Outputs.TRACE.value: trace})

    return ret

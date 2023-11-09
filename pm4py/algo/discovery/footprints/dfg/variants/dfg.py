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
from pm4py.objects.dfg import utils
from enum import Enum
from typing import Optional, Dict, Any, Tuple


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


def apply(dfg: Dict[Tuple[str, str], int], parameters: Optional[Dict[Any, Any]] = None) -> Dict[str, Any]:
    """
    Discovers a footprint object from a DFG

    Parameters
    --------------
    dfg
        DFG
    parameters
        Parameters of the algorithm

    Returns
    --------------
    footprints_obj
        Footprints object
    """
    if parameters is None:
        parameters = {}

    parallel = {(x, y) for (x, y) in dfg if (y, x) in dfg}
    sequence = {(x, y) for (x, y) in dfg if not (y, x) in dfg}
    # replace this if needed
    start_activities = set(utils.dfg_utils.infer_start_activities(dfg))
    # replace this if needed
    end_activities = set(utils.dfg_utils.infer_end_activities(dfg))
    activities = set(utils.dfg_utils.get_activities_from_dfg(dfg))

    return {Outputs.SEQUENCE.value: sequence, Outputs.PARALLEL.value: parallel,
            Outputs.START_ACTIVITIES.value: start_activities, Outputs.END_ACTIVITIES.value: end_activities, Outputs.ACTIVITIES.value: activities}

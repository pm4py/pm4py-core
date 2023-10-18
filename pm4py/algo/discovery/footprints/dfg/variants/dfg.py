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

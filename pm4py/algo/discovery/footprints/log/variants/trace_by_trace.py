from enum import Enum
from pm4py.util import constants
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.algo.discovery.footprints.outputs import Outputs
from pm4py.objects.conversion.log import converter
from pm4py.objects.log.log import EventLog
from pm4py.util import xes_constants
from pm4py.util import exec_utils


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY


def apply(log, parameters=None):
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
        activities = set(x[activity_key] for x in trace)
        if len(trace) > 0:
            start_activities = set([trace[0][activity_key]])
            end_activities = set([trace[-1][activity_key]])
        else:
            start_activities = set()
            end_activities = set()

        ret.append(
            {Outputs.DFG.value: dfg, Outputs.SEQUENCE.value: sequence, Outputs.PARALLEL.value: parallel, Outputs.ACTIVITIES.value: activities,
             Outputs.START_ACTIVITIES.value: start_activities, Outputs.END_ACTIVITIES.value: end_activities,
             Outputs.MIN_TRACE_LENGTH.value: len(trace)})

    return ret

from enum import Enum
from pm4py.util import xes_constants
from pm4py.util import constants
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.algo.discovery.causal import algorithm as causal_discovery
from pm4py.algo.discovery.footprints.outputs import Outputs
from pm4py.statistics.start_activities.log import get as get_start_activities
from pm4py.statistics.end_activities.log import get as get_end_activities
from pm4py.objects.conversion.log import converter
from pm4py.util import exec_utils


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY


def apply(log, parameters=None):
    """
    Discovers a footprint object from an event log
    (the footprints of the event log are returned)

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
        Footprints object
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)

    log = converter.apply(log, variant=converter.TO_EVENT_LOG, parameters=parameters)

    dfg = dfg_discovery.apply(log, parameters=parameters)
    parallel = {(x, y) for (x, y) in dfg if (y, x) in dfg}
    sequence = set(causal_discovery.apply(dfg, causal_discovery.Variants.CAUSAL_ALPHA))

    start_activities = set(get_start_activities.get_start_activities(log, parameters=parameters))
    end_activities = set(get_end_activities.get_end_activities(log, parameters=parameters))
    activities = set(y[activity_key] for x in log for y in x)

    return {Outputs.DFG.value: dfg, Outputs.SEQUENCE.value: sequence, Outputs.PARALLEL.value: parallel,
            Outputs.START_ACTIVITIES.value: start_activities, Outputs.END_ACTIVITIES.value: end_activities,
            Outputs.ACTIVITIES.value: activities,
            Outputs.MIN_TRACE_LENGTH.value: min(len(x) for x in log) if len(log) > 0 else 0}

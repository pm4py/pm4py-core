from enum import Enum
from pm4py.util import constants
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.algo.discovery.footprints.outputs import Outputs
from pm4py.objects.conversion.log import converter
from pm4py.objects.log.log import EventLog


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

    log = converter.apply(log, variant=converter.TO_EVENT_LOG, parameters=parameters)

    ret = []

    for trace in log:
        dfg = dfg_discovery.apply(EventLog([trace]), parameters=parameters)
        parallel = {(x, y) for (x, y) in dfg if (y, x) in dfg}
        sequence = {(x, y) for (x, y) in dfg if not (y, x) in dfg}

        ret.append({Outputs.SEQUENCE.value: sequence, Outputs.PARALLEL.value: parallel})

    return ret


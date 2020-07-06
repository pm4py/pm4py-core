from enum import Enum
from pm4py.util import constants
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.algo.discovery.causal import algorithm as causal_discovery
from pm4py.algo.discovery.footprints.outputs import Outputs
from pm4py.objects.conversion.log import converter


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

    log = converter.apply(log, variant=converter.TO_EVENT_LOG, parameters=parameters)

    dfg = dfg_discovery.apply(log, parameters=parameters)
    parallel = {(x, y) for (x, y) in dfg if (y, x) in dfg}
    sequence = causal_discovery.apply(dfg, causal_discovery.Variants.CAUSAL_ALPHA)

    return {Outputs.SEQUENCE.value: sequence, Outputs.PARALLEL.value: parallel}

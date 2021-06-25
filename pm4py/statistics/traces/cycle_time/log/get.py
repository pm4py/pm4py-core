from pm4py.objects.log.obj import EventLog, Trace
from pm4py.util import exec_utils, constants, xes_constants
from enum import Enum
from pm4py.objects.conversion.log import converter
from pm4py.statistics.traces.cycle_time.util import compute
from typing import Union, Dict, Optional, Any


class Parameters(Enum):
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY


def apply(log_or_trace: Union[Trace, EventLog], parameters: Optional[Dict[str, Any]] = None) -> float:
    """
    Computes the cycle time starting from an event log or a trace object

    The definition that has been followed is the one proposed in:
    https://www.presentationeze.com/presentations/lean-manufacturing-just-in-time/lean-manufacturing-just-in-time-full-details/process-cycle-time-analysis/calculate-cycle-time/#:~:text=Cycle%20time%20%3D%20Average%20time%20between,is%2024%20minutes%20on%20average.

    So:
    Cycle time  = Average time between completion of units.

    Example taken from the website:
    Consider a manufacturing facility, which is producing 100 units of product per 40 hour week.
    The average throughput rate is 1 unit per 0.4 hours, which is one unit every 24 minutes.
    Therefore the cycle time is 24 minutes on average.

    Parameters
    ------------------
    log_or_trace
        Log or trace
    parameters
        Parameters of the algorithm, including:
        - Parameters.START_TIMESTAMP_KEY => the attribute acting as start timestamp
        - Parameters.TIMESTAMP_KEY => the attribute acting as timestamp

    Returns
    ------------------
    cycle_time
        Cycle time
    """
    if parameters is None:
        parameters = {}

    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)

    if type(log_or_trace) is Trace:
        log = EventLog()
        log.append(log_or_trace)
    else:
        log = converter.apply(log_or_trace)

    events = [(x[start_timestamp_key].timestamp(), x[timestamp_key].timestamp()) for trace in log for x in trace]

    return compute.cycle_time(events, len(log))

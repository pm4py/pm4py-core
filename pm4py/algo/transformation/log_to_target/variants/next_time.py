from enum import Enum
from pm4py.util import exec_utils, constants, xes_constants
from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd
from typing import Union, Dict, Optional, Any, Tuple, List
from pm4py.objects.conversion.log import converter as log_converter


class Parameters(Enum):
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY


def apply(log: Union[EventLog, EventStream, pd.DataFrame], parameters: Optional[Dict[Any, Any]] = None) -> Tuple[List[List[int]], List[str]]:
    """
    Returns a list of lists (one for every case of the log) containing the difference between the timestamp of the current event
    and the timestamp of the next event of the case.
    For the last event of the case, the difference is defaulted to 0.

    Parameters
    ---------------
    log
        Event log
    parameters
        Parameters of the algorithm, including:
        - Parameters.TIMESTAMP_KEY => the attribute of the log to be used as timestamp

    Returns
    ---------------
    target
        The aforementioned list
    classes
        Dummy list (of classes)
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)

    target = []
    for trace in log:
        target.append([])
        for i in range(len(trace)):
            curr_time = trace[i][timestamp_key].timestamp()
            next_time = trace[i+1][timestamp_key].timestamp() if i < len(trace)-1 else curr_time

            target[-1].append(next_time-curr_time)

    return target, ["@@next_time"]

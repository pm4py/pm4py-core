from enum import Enum
from pm4py.util import exec_utils, constants, xes_constants
from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd
from typing import Union, Dict, Optional, Any, Tuple, List
from pm4py.objects.conversion.log import converter as log_converter


class Parameters(Enum):
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    ENABLE_PADDING = "enable_padding"


def apply(log: Union[EventLog, EventStream, pd.DataFrame], parameters: Optional[Dict[Any, Any]] = None) -> Tuple[List[List[int]], List[str]]:
    """
    Returns a list of lists (one for every case of the log) containing the difference between the timestamp of the current event
    and the timestamp of the next event of the case (an automatic padding option is also available).
    For the last event of the case, the difference is defaulted to 0.

    Parameters
    ---------------
    log
        Event log
    parameters
        Parameters of the algorithm, including:
        - Parameters.TIMESTAMP_KEY => the attribute of the log to be used as timestamp
        - Parameters.ENABLE_PADDING => enables the padding (the length of cases is normalized)

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
    max_case_length = max([len(x) for x in log])

    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)
    enable_padding = exec_utils.get_param_value(Parameters.ENABLE_PADDING, parameters, False)

    target = []
    for trace in log:
        target.append([])
        for i in range(len(trace)):
            curr_time = trace[i][timestamp_key].timestamp()
            next_time = trace[i+1][timestamp_key].timestamp() if i < len(trace)-1 else curr_time
            target[-1].append(float(next_time-curr_time))
        if enable_padding:
            while len(target[-1]) < max_case_length:
                target[-1].append(0.0)

    return target, ["@@next_time"]

from enum import Enum
from pm4py.util import exec_utils, constants, xes_constants
from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd
from typing import Union, Dict, Optional, Any
from pm4py.objects.conversion.log import converter as log_converter


class Parameters(Enum):
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY


def apply(log: Union[EventLog, EventStream, pd.DataFrame], parameters: Optional[Dict[Any, Any]] = None):
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)

    target = []
    for trace in log:
        target.append([])
        for i in range(len(trace)):
            curr_time = trace[i][timestamp_key].timestamp()
            last_time = trace[-1][timestamp_key].timestamp()

            target[-1].append(last_time-curr_time)

    return target, ["@@remaining_time"]

from enum import Enum
from pm4py.util import exec_utils, constants, xes_constants
from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd
from typing import Union, Dict, Optional, Any, Tuple, List
from pm4py.objects.conversion.log import converter as log_converter


class Parameters(Enum):
    ACTIVITIES = "activities"
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY


def apply(log: Union[EventLog, EventStream, pd.DataFrame], parameters: Optional[Dict[Any, Any]] = None) -> Tuple[List[List[List[int]]], List[str]]:
    """
    Returns a list of matrixes (one for every case).
    Every matrix contains as many rows as many events are contained in the case,
    and as many columns as many distinct activities are in the log.

    The corresponding activity to the given event is assigned to the value 1;
    the remaining activities are assigned to the value 0.

    Parameters
    --------------
    log
        Event log / Event stream / Pandas dataframe
    parameters
        Parameters of the algorithm, including:
        - Parameters.ACTIVITIES => list of activities to consider
        - Parameters.ACTIVITY_KEY => attribute that should be used as activity

    Returns
    -------------
    target
        The aforementioned list of matrixes.
    activities
        The considered list of activities
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    activities = exec_utils.get_param_value(Parameters.ACTIVITIES, parameters, sorted(list(set(y[activity_key] for x in log for y in x))))

    target = []
    for trace in log:
        target.append([])
        for i in range(len(trace)):
            target[-1].append([0] * len(activities))
            if i < len(trace) - 1:
                act = trace[i+1][activity_key]
                if act in activities:
                    target[-1][-1][activities.index(act)] = 1

    return target, activities

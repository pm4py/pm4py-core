from pm4py.util import constants, xes_constants, exec_utils
from enum import Enum
from collections import Counter
from pm4py.objects.log.obj import EventLog, EventStream
from typing import Union, Optional, Dict, Any
from pm4py.objects.conversion.log import converter as log_converter


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY


def apply(log: Union[EventLog, EventStream], parameters: Optional[Dict[str, Any]] = None) -> Dict[str, int]:
    """
    Associates to each activity (with at least one rework) the number of cases in the log for which
    the rework happened.

    Parameters
    ------------------
    log
        Event log
    parameters
        Parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY => the attribute to be used as activity

    Returns
    ------------------
    dict
        Dictionary associating to each activity the number of cases for which the rework happened
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log)

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    ret = Counter()

    for trace in log:
        activities = Counter([x[activity_key] for x in trace])
        activities = [x for x in activities if activities[x] > 1]
        for act in activities:
            ret[act] += 1

    return dict(ret)

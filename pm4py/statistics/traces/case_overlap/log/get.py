from enum import Enum
from typing import Dict, Optional, Any, List

from pm4py.objects.log.obj import EventLog
from pm4py.statistics.traces.case_overlap.utils import compute
from pm4py.util import exec_utils, constants, xes_constants
from pm4py.objects.conversion.log import converter


class Parameters(Enum):
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY


def apply(log: EventLog, parameters: Optional[Dict[str, Any]] = None) -> List[int]:
    """
    Computes the case overlap statistic from an interval event log

    Parameters
    -----------------
    log
        Interval event log
    parameters
        Parameters of the algorithm, including:
        - Parameters.TIMESTAMP_KEY => attribute representing the completion timestamp
        - Parameters.START_TIMESTAMP_KEY => attribute representing the start timestamp

    Returns
    ----------------
    case overlap
        List associating to each case the number of open cases during the life of a case
    """
    if parameters is None:
        parameters = {}

    log = converter.apply(log, parameters=parameters)

    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters,
                                                     xes_constants.DEFAULT_TIMESTAMP_KEY)

    points = []
    for trace in log:
        case_points = []
        for event in trace:
            case_points.append((event[start_timestamp_key].timestamp(), event[timestamp_key].timestamp()))
        points.append((min(x[0] for x in case_points), max(x[1] for x in case_points)))

    return compute.apply(points, parameters=parameters)

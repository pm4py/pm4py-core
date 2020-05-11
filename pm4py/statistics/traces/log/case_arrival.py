from pm4py.util.xes_constants import DEFAULT_TIMESTAMP_KEY
import statistics
from pm4py.util.business_hours import BusinessHours
from pm4py.util import exec_utils, constants
from enum import Enum


class Parameters(Enum):
    ATTRIBUTE_KEY = constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY

    BUSINESS_HOURS = "business_hours"
    WORKTIMING = "worktiming"
    WEEKENDS = "weekends"


def get_case_arrival_avg(log, parameters=None):
    """
    Gets the average time interlapsed between case starts

    Parameters
    --------------
    log
        Trace log
    parameters
        Parameters of the algorithm, including:
            Parameters.TIMESTAMP_KEY -> attribute of the log to be used as timestamp

    Returns
    --------------
    case_arrival_avg
        Average time interlapsed between case starts
    """
    if parameters is None:
        parameters = {}
    business_hours = exec_utils.get_param_value(Parameters.BUSINESS_HOURS, parameters, False)
    worktiming = exec_utils.get_param_value(Parameters.WORKTIMING, parameters, [7, 17])
    weekends = exec_utils.get_param_value(Parameters.WEEKENDS, parameters, [6, 7])

    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY)

    case_start_time = [trace[0][timestamp_key] for trace in log if trace and timestamp_key in trace[0]]
    case_start_time = sorted(case_start_time)

    case_diff_start_time = []
    for i in range(len(case_start_time)-1):
        if business_hours:
            bh = BusinessHours(case_start_time[i].replace(tzinfo=None), case_start_time[i+1].replace(tzinfo=None), worktiming=worktiming,
                               weekends=weekends)
            case_diff_start_time.append(bh.getseconds())
        else:
            case_diff_start_time.append((case_start_time[i+1]-case_start_time[i]).total_seconds())

    if case_diff_start_time:
        return statistics.median(case_diff_start_time)

    return 0.0


def get_case_dispersion_avg(log, parameters=None):
    """
    Gets the average time interlapsed between case ends

    Parameters
    --------------
    log
        Trace log
    parameters
        Parameters of the algorithm, including:
            Parameters.TIMESTAMP_KEY -> attribute of the log to be used as timestamp

    Returns
    --------------
    case_arrival_avg
        Average time interlapsed between case starts
    """
    if parameters is None:
        parameters = {}
    business_hours = exec_utils.get_param_value(Parameters.BUSINESS_HOURS, parameters, False)
    worktiming = exec_utils.get_param_value(Parameters.WORKTIMING, parameters, [7, 17])
    weekends = exec_utils.get_param_value(Parameters.WEEKENDS, parameters, [6, 7])

    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY)

    case_end_time = [trace[-1][timestamp_key] for trace in log if trace and timestamp_key in trace[0]]
    case_end_time = sorted(case_end_time)

    case_diff_end_time = []
    for i in range(len(case_end_time)-1):
        if business_hours:
            bh = BusinessHours(case_end_time[i].replace(tzinfo=None), case_end_time[i+1].replace(tzinfo=None), worktiming=worktiming,
                               weekends=weekends)
            case_diff_end_time.append(bh.getseconds())
        else:
            case_diff_end_time.append((case_end_time[i+1]-case_end_time[i]).total_seconds())

    if case_diff_end_time:
        return statistics.median(case_diff_end_time)

    return 0.0

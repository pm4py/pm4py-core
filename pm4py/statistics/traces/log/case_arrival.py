from pm4py.util.xes_constants import DEFAULT_TIMESTAMP_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_TIMESTAMP_KEY
import statistics
from pm4py.util.business_hours import BusinessHours


def get_case_arrival_avg(log, parameters=None):
    """
    Gets the average time interlapsed between case starts

    Parameters
    --------------
    log
        Trace log
    parameters
        Parameters of the algorithm, including:
            PARAMETER_CONSTANT_TIMESTAMP_KEY -> attribute of the log to be used as timestamp

    Returns
    --------------
    case_arrival_avg
        Average time interlapsed between case starts
    """
    if parameters is None:
        parameters = {}
    business_hours = parameters["business_hours"] if "business_hours" in parameters else False
    worktiming = parameters["worktiming"] if "worktiming" in parameters else [7, 17]
    weekends = parameters["weekends"] if "weekends" in parameters else [6, 7]

    timestamp_key = parameters[
        PARAMETER_CONSTANT_TIMESTAMP_KEY] if PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else DEFAULT_TIMESTAMP_KEY

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
            PARAMETER_CONSTANT_TIMESTAMP_KEY -> attribute of the log to be used as timestamp

    Returns
    --------------
    case_arrival_avg
        Average time interlapsed between case starts
    """
    if parameters is None:
        parameters = {}
    business_hours = parameters["business_hours"] if "business_hours" in parameters else False
    worktiming = parameters["worktiming"] if "worktiming" in parameters else [7, 17]
    weekends = parameters["weekends"] if "weekends" in parameters else [6, 7]

    timestamp_key = parameters[
        PARAMETER_CONSTANT_TIMESTAMP_KEY] if PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else DEFAULT_TIMESTAMP_KEY

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
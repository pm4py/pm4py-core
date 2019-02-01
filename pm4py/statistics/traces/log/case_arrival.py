from pm4py.objects.log.util.xes import DEFAULT_TIMESTAMP_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_TIMESTAMP_KEY
import statistics


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

    timestamp_key = parameters[
        PARAMETER_CONSTANT_TIMESTAMP_KEY] if PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else DEFAULT_TIMESTAMP_KEY

    case_start_time = [trace[0][timestamp_key] for trace in log if trace and timestamp_key in trace[0]]
    case_start_time = sorted(case_start_time)

    case_diff_start_time = []
    for i in range(len(case_start_time)-1):
        case_diff_start_time.append((case_start_time[i+1]-case_start_time[i]).total_seconds())

    if case_diff_start_time:
        return statistics.mean(case_diff_start_time)

    return 0.0

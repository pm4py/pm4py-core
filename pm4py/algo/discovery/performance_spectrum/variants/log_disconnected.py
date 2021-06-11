from pm4py.objects.log.util import sorting
from pm4py.objects.log.util import basic_filter
from pm4py.util import points_subset
from pm4py.util import xes_constants as xes
from pm4py.util import exec_utils
from enum import Enum
from pm4py.util import constants
from pm4py.util.constants import CASE_CONCEPT_NAME


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    PARAMETER_SAMPLE_SIZE = "sample_size"



def apply(log, list_activities, sample_size, parameters):
    """
    Finds the disconnected performance spectrum provided a log
    and a list of activities

    Parameters
    -------------
    log
        Log
    list_activities
        List of activities interesting for the performance spectrum (at least two)
    sample_size
        Size of the sample
    parameters
        Parameters of the algorithm,  including:
            - Parameters.ACTIVITY_KEY
            - Parameters.TIMESTAMP_KEY

    Returns
    -------------
    points
        Points of the performance spectrum
    """
    if parameters is None:
        parameters = {}

    all_acti_combs = [list_activities[j:j + i] for i in range(2, len(list_activities) + 1) for j in range(0, len(list_activities) - i + 1)]
    two_acti_combs = [[list_activities[i], list_activities[i + 1]] for i in range(len(list_activities) - 1)]

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes.DEFAULT_TIMESTAMP_KEY)
    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, xes.DEFAULT_TRACEID_KEY)
    
    log = sorting.sort_timestamp_log(log, timestamp_key=timestamp_key)
    log = basic_filter.filter_log_events_attr(log, list_activities, parameters=parameters)

    points = []
    for trace in log:
        matches = [(i, i + 1) for i in range(len(trace) - 1) if [trace[i][activity_key], trace[i + 1][activity_key]] in two_acti_combs]

        i = 0
        while i < len(matches) - 1:
            matchAct = [trace[mi][activity_key] for mi in (matches[i] + matches[i + 1][1:])]
            if matches[i][-1] == matches[i + 1][0] and matchAct in all_acti_combs:
                matches[i] = matches[i] + matches[i + 1][1:]
                del matches[i + 1]
                i = 0
            else:
                i += 1

        if matches:
            matches = set(matches)
            timest_comb = [{ 'points': [(trace[i][activity_key], trace[i][timestamp_key].timestamp()) for i in match]} for match in matches]
            for p in timest_comb:
                p['case_id'] = trace.attributes[case_id_key]

            points += timest_comb

    points = sorted(points, key=lambda x: min(x['points'], key=lambda x: x[1])[1])

    if len(points) > sample_size:
        points = points_subset.pick_chosen_points_list(sample_size, points)

    return points


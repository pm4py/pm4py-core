from pm4py.util import constants
from pm4py.objects.log.util import sorting
from pm4py.objects.log.util import basic_filter
from pm4py.util import points_subset
from pm4py.util import xes_constants as xes
from pm4py.statistics.performance_spectrum.parameters import Parameters
from pm4py.util import exec_utils


def apply(log, list_activities, sample_size, parameters):
    """
    Finds the performance spectrum provided a log
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

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes.DEFAULT_TIMESTAMP_KEY)
    
    log = sorting.sort_timestamp_log(log, timestamp_key=timestamp_key)
    parameters[Parameters.ATTRIBUTE_KEY] = activity_key
    log = basic_filter.filter_log_events_attr(log, list_activities, parameters=parameters)

    points = []

    for trace in log:
        for i in range(len(trace)-len(list_activities)+1):
            acti_comb = [event[activity_key] for event in trace[i:i+len(list_activities)]]

            if acti_comb == list_activities:
                timest_comb = [event[timestamp_key].timestamp() for event in trace[i:i+len(list_activities)]]

                points.append(timest_comb)

    points = sorted(points, key=lambda x: x[0])

    if len(points) > sample_size:
        points = points_subset.pick_chosen_points_list(sample_size, points)

    return points

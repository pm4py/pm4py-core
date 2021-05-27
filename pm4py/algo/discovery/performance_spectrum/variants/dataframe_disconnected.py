from pm4py.util import xes_constants as xes
from pm4py.util import exec_utils, pandas_utils, constants


from enum import Enum
from pm4py.util import constants, points_subset

import numpy as np

class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    PARAMETER_SAMPLE_SIZE = "sample_size"


def gen_patterns(pattern, length):
    return [pattern[i:i+length] for i in range(len(pattern) - (length - 1))]

def apply(dataframe, list_activities, sample_size, parameters):
    """
    Finds the disconnected performance spectrum provided a dataframe
    and a list of activities

    Parameters
    -------------
    dataframe
        Dataframe
    list_activities
        List of activities interesting for the performance spectrum (at least two)
    sample_size
        Size of the sample
    parameters
        Parameters of the algorithm,  including:
            - Parameters.ACTIVITY_KEY
            - Parameters.TIMESTAMP_KEY
            - Parameters.CASE_ID_KEY

    Returns
    -------------
    points
        Points of the performance spectrum
    """
    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes.DEFAULT_TIMESTAMP_KEY)

    dataframe = dataframe[[case_id_glue, activity_key, timestamp_key]]
    dataframe = dataframe[dataframe[activity_key].isin(list_activities)]
    dataframe = pandas_utils.insert_index(dataframe, constants.DEFAULT_EVENT_INDEX_KEY)
    dataframe = dataframe.sort_values([case_id_glue, timestamp_key, constants.DEFAULT_EVENT_INDEX_KEY])
    dataframe[timestamp_key] = dataframe[timestamp_key].astype(np.int64) / 10**9
    
    all_patterns = [(len(list_activities) - i, gen_patterns(list_activities, len(list_activities) - i)) for i in range(len(list_activities) - 1)]

    all_matches = {}
    for name, group in dataframe.groupby(case_id_glue):
        for l, patterns in all_patterns:
            matches = [group[[activity_key, timestamp_key]].iloc[i:i + l] for i in range(0, len(group) - l + 1) if list(group[activity_key][i: i + l]) in patterns]
            
            # prevent subpatterns from including these events again
            for match in matches:
                group = group.drop(match.index, errors='ignore')

            if matches:
                all_matches[name] = all_matches.get(name, []) + matches
    
    points = []
    for case_id, matches in all_matches.items():
        for match in matches:
            match = match.set_index(activity_key)
            points.append({'case_id': case_id, 'points': list(match.itertuples(name=None))})

    if len(points) > sample_size:
        points = points_subset.pick_chosen_points_list(sample_size, points)

    return points


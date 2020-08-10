from pm4py.util import exec_utils
from enum import Enum
from pm4py.util import constants, xes_constants
from pm4py.objects.conversion.log import converter
from pm4py.algo.discovery.correlation_mining.versions import classic
from collections import Counter
import numpy as np
import pandas as pd


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    SAMPLE_SIZE = "sample_size"


def apply(log, parameters=None):
    """
    Applies the correlation miner (splits the log in smaller chunks)

    Parameters
    ---------------
    log
        Log object
    parameters
        Parameters of the algorithm

    Returns
    ---------------
    dfg
        Frequency DFG
    performance_dfg
        Performance DFG
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters,
                                                     xes_constants.DEFAULT_TIMESTAMP_KEY)
    sample_size = exec_utils.get_param_value(Parameters.SAMPLE_SIZE, parameters, 100000)

    PS_matrixes = []
    duration_matrixes = []

    if type(log) is pd.DataFrame:
        # keep only the two columns before conversion
        log = log[list(set([activity_key, timestamp_key, start_timestamp_key]))]
        log = log.sort_values([timestamp_key, start_timestamp_key])
        activities_counter = dict(log[activity_key].value_counts())
        activities = sorted(list(activities_counter.keys()))
    else:
        log = converter.apply(log, variant=converter.Variants.TO_EVENT_STREAM)
        activities_counter = Counter(x[activity_key] for x in log)
        activities = sorted(list(activities_counter.keys()))

    prev = 0
    while prev < len(log):
        sample = log[prev:min(len(log), prev + sample_size)]
        transf_stream, activities_grouped, activities = classic.preprocess_log(sample, activities=activities,
                                                                               parameters=parameters)
        PS_matrix, duration_matrix = classic.get_PS_dur_matrix(activities_grouped, activities,
                                                               parameters=parameters)
        PS_matrixes.append(PS_matrix)
        duration_matrixes.append(duration_matrix)

        prev = prev + sample_size

    PS_matrix = np.zeros((len(activities), len(activities)))
    duration_matrix = np.zeros((len(activities), len(activities)))
    z = 0
    while z < len(PS_matrixes):
        PS_matrix = PS_matrix + PS_matrixes[z]
        duration_matrix = np.maximum(duration_matrix, duration_matrixes[z])
        z = z + 1
    PS_matrix = PS_matrix / float(len(PS_matrixes))

    return classic.resolve_lp_get_dfg(PS_matrix, duration_matrix, activities, activities_counter)

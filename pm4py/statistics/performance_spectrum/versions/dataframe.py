from pm4py.util import xes_constants as xes
from pm4py.util.constants import CASE_CONCEPT_NAME
import pandas as pd
import numpy as np
from pm4py.statistics.performance_spectrum.parameters import Parameters
from pm4py.util import exec_utils, pandas_utils, constants


def apply(dataframe, list_activities, sample_size, parameters):
    """
    Finds the performance spectrum provided a dataframe
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

    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes.DEFAULT_TIMESTAMP_KEY)

    dataframe = dataframe[[case_id_glue, activity_key, timestamp_key]]
    dataframe = dataframe[dataframe[activity_key].isin(list_activities)]
    dataframe = pandas_utils.insert_index(dataframe, constants.DEFAULT_EVENT_INDEX_KEY)
    dataframe = dataframe.sort_values([case_id_glue, timestamp_key, constants.DEFAULT_EVENT_INDEX_KEY])
    dataframe[timestamp_key] = dataframe[timestamp_key].astype(np.int64) / 10**9
    list_replicas = []
    activity_names = []
    filt_col_names = []
    for i in range(len(list_activities)):
        if i > 0:
            dataframe = dataframe.shift(-1)
            activity_names.append("+'@@'+")
        ren = {x: x+"_"+str(i) for x in dataframe.columns}
        list_replicas.append(dataframe.rename(columns=ren))
        filt_col_names.append(timestamp_key+"_"+str(i))

        activity_names.append("dataframe[activity_key+'_"+str(i)+"']")

    dataframe = pd.concat(list_replicas, axis=1)
    for i in range(len(list_activities)-1):
        dataframe = dataframe[dataframe[case_id_glue+"_"+str(i)] == dataframe[case_id_glue+"_"+str(i+1)]]
    dataframe["@@merged_activity"] = eval("".join(activity_names))
    desidered_act = "@@".join(list_activities)
    dataframe = dataframe[dataframe["@@merged_activity"] == desidered_act]
    dataframe = dataframe[filt_col_names]

    if len(dataframe) > sample_size:
        dataframe = dataframe.sample(n=sample_size)

    points = pandas_utils.to_dict_records(dataframe)
    points = [[p[tk] for tk in filt_col_names] for p in points]
    points = sorted(points, key=lambda x: x[0])

    return points


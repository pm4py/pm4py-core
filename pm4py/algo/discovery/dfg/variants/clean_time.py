import time
from enum import Enum
from typing import List, Optional, Dict, Any

import pandas as pd
import numpy as np
from pandas._libs.tslibs.timestamps import Timestamp
from pandas.core.frame import DataFrame
from pandas.core.tools.datetimes import to_datetime

from pm4py.objects.dfg.obj import DFG
from pm4py.util import constants, exec_utils
from pm4py.util import xes_constants as xes_util


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY


CONST_AUX_ACT = 'aux_act_'
CONST_AUX_CASE = 'aux_case_'
CONST_COUNT = 'count_'


def apply(log : pd.DataFrame, parameters):
    parameters = {} if parameters is None else parameters
    act_key = exec_utils.get_param_value(
        Parameters.ACTIVITY_KEY, parameters, xes_util.DEFAULT_NAME_KEY)
    cid_key = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, constants.CASE_ATTRIBUTE_GLUE)
    time_key = exec_utils.get_param_value(
        Parameters.TIMESTAMP_KEY, parameters, xes_util.DEFAULT_TIMESTAMP_KEY)
    aux_act = CONST_AUX_ACT + str(time.time())
    aux_case = CONST_AUX_CASE + str(time.time())
    count = CONST_COUNT + str(time.time())
    cid_timestamp = 'cid_wise_start_time'
    relative_time = 'relative_time'

    df = log.sort_values([cid_key, time_key]).loc[:, [cid_key, act_key]].reset_index()
    df[aux_act] = df[act_key].shift(-1)
    df[aux_case] = df[cid_key].shift(-1)
    dfg = DFG()

    excl_starter = df.at[0, act_key]
    borders = df[(df[cid_key] != df[aux_case])]
    starters = borders.groupby([aux_act]).size().reset_index()
    starters.columns = [aux_act, count]
    starters.loc[starters[aux_act] == excl_starter, count] += 1

    df = df[(df[cid_key] == df[aux_case])]
    
    for (a, b, f) in list(df.groupby([act_key, aux_act]).size(
    ).reset_index().itertuples(index=False, name=None)):
        dfg.graph[(a, b)] += f

    for (a, f) in list(starters.itertuples(index=False, name=None)):
        dfg.start_activities[a] += f

    for (a, f) in list(borders.groupby(
            [act_key]).size().reset_index().itertuples(index=False, name=None)):
        dfg.end_activities[a] += f


    #Realtive Time Specific Code 
    df = log.sort_values([cid_key, time_key]).loc[:, [cid_key, act_key, time_key]].reset_index()

    #Change the start_actvitiy to a dictionary for >1 start activity
    start_activities = dfg.start_activities
    start_activity =""
    for key, value in start_activities.items():
        start_activity = key 
    
    all_act = get_all_activities(df, act_key)
    all_cid = get_all_traces(df, cid_key)
    cid_wise_start_time = get_cid_wise_start_time( df, act_key, cid_key, time_key, all_cid, start_activity)
    df[cid_timestamp] = df[cid_key].map(cid_wise_start_time)
    df[relative_time] = df[time_key] - df[cid_timestamp]

    time_dictionary = {}

    for act in all_act:  
        aux_df = df[df[act_key] == act] 
        mean = avg_relative_time(aux_df, relative_time)
        time_dictionary[act] = mean
    
    return time_dictionary


def avg_relative_time(df : pd.DataFrame, relative_time) -> Timestamp:
    mean = df[relative_time].mean()
    return mean


def get_cid_wise_start_time(df : pd.DataFrame, act_key,cid_key, time_key, all_cid : List, start_activity) -> Dict:
    cid_time_dic = {}
    for cid in all_cid:
        aux_df = df[df[cid_key] == cid]
        time_value = aux_df.loc[aux_df[act_key] == start_activity, time_key]
        start_time = 0
        for i in time_value:
            start_time = i
        cid_time_dic[cid] = start_time
    return cid_time_dic
        

def get_all_traces(df : pd.DataFrame, cid_key) -> List:
    return np.unique(df[cid_key])

    
def get_all_activities (df : pd.DataFrame, act_key) -> list:
    return np.unique(df[act_key])

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


from pm4py.discovery import discover_dfg_typed

def apply(log: pd.DataFrame, parameters):
    #print("new function")
    #dfg, start_act, end_act = discover_dfg_typed(log)
    ##print(log[:20])

    act_key = exec_utils.get_param_value(
        Parameters.ACTIVITY_KEY, parameters, xes_util.DEFAULT_NAME_KEY)
    cid_key = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, constants.CASE_ATTRIBUTE_GLUE)
    time_key = exec_utils.get_param_value(
        Parameters.TIMESTAMP_KEY, parameters, xes_util.DEFAULT_TIMESTAMP_KEY)

    #sort the values according to cid and timekey
    df = log.sort_values([cid_key, time_key]).loc[:, [cid_key, act_key, time_key]].reset_index()
    #print(df[:20])

    #mapping each case ID to the first time stamp of that case.
    case_starttime_map ={}
    grouped = df.groupby(cid_key)
    #print(grouped)
    all_cases = df[cid_key].unique()
    #print(all_cases)

    '''
    1. get each group of cid
    2. save variables - first row's activity and first row's timestamp(init_timestamp)
    3. get all act in this case as a list
    4. for each act in this case, calculate the average timestmaps (This is for loops)
        - average out the timestamp for this activity (loop_act_timestamp)
        - 
    
    5.. use the init_timestamp to calculate the relative time  
    '''

    time_dictionary_list = {}

    for case in all_cases:
        ##print(case)
        current_group = grouped.get_group(case)
        current_group = current_group.sort_values([cid_key, time_key]).loc[:, [cid_key, act_key, time_key]].reset_index()
        #print(current_group)
       
        ##print(f"First row's activity of this group\n{current_group[act_key][0]}")
        ##print(f"First row's timestamp of this group\n{current_group[time_key][0]}")
        
        all_act = current_group[act_key].unique()
        #print(all_act)
        init_timestamp = current_group[time_key][0]
        #deal with loops in a case
        for act in all_act:
            #print(act)
            curr_act = act
            df1 = current_group[current_group[act_key] == act]
            #print(df1)
            mean_time = df1[time_key].mean()
            #print(f"Mean time for this df is {mean_time}")
            average_time = mean_time - init_timestamp
            
            #print(f"Start timestamp is {init_timestamp}")
            #print(f"Average timestamp is {average_time}")
            #print()

            if act not in time_dictionary_list.keys():
                time_dictionary_list[act] = []
                time_dictionary_list[act].append(average_time)
            else:
                time_dictionary_list[act].append(average_time)
            
        #print()
        #print()
        #print()

    print(time_dictionary_list.keys())
    print(time_dictionary_list)
    keys = time_dictionary_list.keys()

    time_dictionary = {}
    for key in keys:
        print(key)
        #print(time_dictionary_list[key])
        #average = sum(time_dictionary_list[key]) / len(time_dictionary_list[key])
        #print(average)
        avg=pd.to_timedelta(pd.Series(time_dictionary_list[key])).mean()
        print(avg)
        time_dictionary[key] = avg 
        print()

    print(time_dictionary)

        

    #df_time = pd.DataFrame(data=time_dictionary_list)
    #print(df_time)
    return time_dictionary






def apply1(log : pd.DataFrame, parameters):
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

    #print("Finished old clean_code")
    if(len(dfg.start_activities)>1):
        #print("Not possible for more than one start activity")
        return
    

    #Realtive Time Specific Code 
    df = log.sort_values([cid_key, time_key]).loc[:, [cid_key, act_key, time_key]].reset_index()

    #Change the start_actvitiy to a dictionary for >1 start activity
    start_activities = dfg.start_activities
    start_activity =""
    for key, value in start_activities.items():
        start_activity = key 
    
    #print("Starting to get all activities")

    all_act = get_all_activities(df, act_key)
    #print("Starting to get all traces")
    all_cid = get_all_traces(df, cid_key)
    #print("Starting to get cid_wise_start_time activities")
    cid_wise_start_time = get_cid_wise_start_time( df, act_key, cid_key, time_key, all_cid, start_activity)
    #print("Starting to map keys")
    df[cid_timestamp] = df[cid_key].map(cid_wise_start_time)
    #print(df)
    ##print(df[time_key][1] ,type(df[time_key][1]), df[cid_timestamp][1] ,type(df[cid_timestamp][1]))
    ##print(df[time_key], df[cid_timestamp] )

    df[relative_time] = df[time_key] - df[cid_timestamp]
    #print(df[0:6])

    #print(df[:6].to_markdown()) 

    time_dictionary = {}
    #print("Starting to get average relative time activities")
    for act in all_act:  
        aux_df = df[df[act_key] == act] 
        #print("inside for to get avg to get all activities")
        mean = avg_relative_time(aux_df, relative_time)
        time_dictionary[act] = mean

    #print("finished clean_time")
    return time_dictionary


def avg_relative_time(df : pd.DataFrame, relative_time) -> Timestamp:
    mean = df[relative_time].mean()
    return mean


def get_cid_wise_start_time(df : pd.DataFrame, act_key,cid_key, time_key, all_cid : List, start_activity) -> Dict:
    cid_time_dic = {}
    #print("Starting for loops")
    #print(len(all_cid))
    for cid in all_cid:
        #print(f"{cid} in {all_cid}")
        aux_df = df[df[cid_key] == cid]
        #print(aux_df)
        
        time_value = aux_df.loc[aux_df[act_key] == start_activity, time_key]
        #print("time value is : ",time_value)
        #start_time = 0
        start_time = pd.Timestamp(0)
        #print( "start time : ",start_time)
        for i in time_value:
            start_time = i
            #print("start time : ",start_time)
        cid_time_dic[cid] = start_time
        break
        ##print()
        
        
        
    #print("finished get_cid_wise_start")
    return cid_time_dic
        

def get_all_traces(df : pd.DataFrame, cid_key) -> List:
    return np.unique(df[cid_key])

    
def get_all_activities (df : pd.DataFrame, act_key) -> list:
    return np.unique(df[act_key])

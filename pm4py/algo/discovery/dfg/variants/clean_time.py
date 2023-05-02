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
            

    print(time_dictionary_list.keys())
    #print(time_dictionary_list)
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

    return time_dictionary


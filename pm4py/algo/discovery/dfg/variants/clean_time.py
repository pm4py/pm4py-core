'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''

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


def apply(log: pd.DataFrame, parameters=None):
    if parameters is None:
        parameters = {}

    act_key = exec_utils.get_param_value(
        Parameters.ACTIVITY_KEY, parameters, xes_util.DEFAULT_NAME_KEY)
    cid_key = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, constants.CASE_ATTRIBUTE_GLUE)
    time_key = exec_utils.get_param_value(
        Parameters.TIMESTAMP_KEY, parameters, xes_util.DEFAULT_TIMESTAMP_KEY)

    '''sort the values according to cid and timekey'''
    df = log.sort_values([cid_key, time_key]).loc[:, [cid_key, act_key, time_key]].reset_index()

    '''mapping each case ID to the first time stamp of that case.'''
    grouped = df.groupby(cid_key)
    all_cases = df[cid_key].unique()

    time_dictionary_list = {}

    for case in all_cases:
        current_group = grouped.get_group(case)
        current_group = current_group.sort_values([cid_key, time_key]).loc[:, [cid_key, act_key, time_key]].reset_index()
       
        all_act = current_group[act_key].unique()
        init_timestamp = current_group[time_key][0]
        '''deal with loops in a case'''
        for act in all_act:
            df1 = current_group[current_group[act_key] == act]
            mean_time = df1[time_key].mean()
            average_time = mean_time - init_timestamp

            if act not in time_dictionary_list.keys():
                time_dictionary_list[act] = []
                time_dictionary_list[act].append(average_time)
            else:
                time_dictionary_list[act].append(average_time)
            

    keys = time_dictionary_list.keys()
    time_dictionary = {}
    for key in keys:
        avg=pd.to_timedelta(pd.Series(time_dictionary_list[key])).mean()
        time_dictionary[key] = avg 

    return time_dictionary


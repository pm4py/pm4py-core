import time
from enum import Enum
from typing import Optional, Dict, Any

import numpy as np
import pandas as pd

from pm4py.objects.dfg.obj import DFG
from pm4py.util import constants, exec_utils
from pm4py.util import xes_constants as xes_util


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY


CONST_AUX_ACT_START = 'aux_act_start'
CONST_PROCESS_START = '#!$#PROCESS_START#!$#'
CONST_AUX_ACT_END = 'aux_act_end'
CONST_PROCESS_END = '#!$#PROCESS_END#!$#'


def apply(log: pd.DataFrame, parameters: Optional[Dict[str, Any]] = None) -> DFG:
    parameters = {} if parameters is None else parameters
    act_key = exec_utils.get_param_value(
        Parameters.ACTIVITY_KEY, parameters, xes_util.DEFAULT_NAME_KEY)
    cid_key = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, constants.CASE_ATTRIBUTE_GLUE)
    time_key = exec_utils.get_param_value(
        Parameters.TIMESTAMP_KEY, parameters, xes_util.DEFAULT_TIMESTAMP_KEY)

    df = log.sort_values([cid_key, time_key]).loc[:, [cid_key, act_key]].reset_index()

    aux_act_start = CONST_AUX_ACT_START + str(time.time())
    aux_act_end = CONST_AUX_ACT_END + str(time.time())
    df[aux_act_start] = df.groupby(cid_key)[act_key].shift(1).replace(np.nan, CONST_PROCESS_START)
    df[aux_act_end] = df.groupby(cid_key)[act_key].shift(-1).replace(np.nan, CONST_PROCESS_END)

    starters = df[(df[aux_act_start] == CONST_PROCESS_START)]
    borders = df[(df[aux_act_end] == CONST_PROCESS_END)]
    connections = df[((df[aux_act_start] != CONST_PROCESS_START) & (df[aux_act_end] != CONST_PROCESS_END))]

    dfg = DFG()

    for (a, b, f) in list(
            connections.groupby([act_key, aux_act_end]).size().reset_index().itertuples(index=False, name=None)):
        dfg.graph[(a, b)] += f

    for (a, f) in list(starters.groupby([act_key]).size().reset_index().itertuples(index=False, name=None)):
        dfg.start_activities[a] += f

    for (a, f) in list(borders.groupby([act_key]).size().reset_index().itertuples(index=False, name=None)):
        dfg.end_activities[a] += f

    return dfg

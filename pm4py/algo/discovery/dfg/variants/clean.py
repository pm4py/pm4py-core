import time
from enum import Enum
from typing import Optional, Dict, Any

import pandas as pd

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


def apply(log: pd.DataFrame, parameters: Optional[Dict[str, Any]] = None) -> DFG:
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
    df = log.sort_values([cid_key, time_key]).loc[:, [cid_key, act_key]]
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

    return dfg

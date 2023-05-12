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
from typing import Optional, Dict, Any

import polars as pl

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


def apply(log: pl.DataFrame, parameters: Optional[Dict[str, Any]] = None) -> DFG:
    parameters = {} if parameters is None else parameters
    act_key = exec_utils.get_param_value(
        Parameters.ACTIVITY_KEY, parameters, xes_util.DEFAULT_NAME_KEY)
    cid_key = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, constants.CASE_ATTRIBUTE_GLUE)
    time_key = exec_utils.get_param_value(
        Parameters.TIMESTAMP_KEY, parameters, xes_util.DEFAULT_TIMESTAMP_KEY)
    aux_act = CONST_AUX_ACT + str(time.time())
    aux_case = CONST_AUX_CASE + str(time.time())
    df = log[[cid_key, act_key, time_key]].clone()
    df = df.sort([cid_key, time_key])
    df = df[[cid_key, act_key]]
    df = df.with_column(df[act_key].shift(-1).alias(aux_act))
    df = df.with_column(df[cid_key].shift(-1).alias(aux_case))
    dfg = DFG()

    excl_starter = df[0, act_key]
    borders = df.filter(df[cid_key] != df[aux_case])

    for d in filter(lambda d: d[aux_act] is not None, borders.groupby([aux_act]).count().to_dicts()):
        v = d['count'] + 1 if d[aux_act] == excl_starter else d['count']
        dfg.start_activities[d[aux_act]] = v

    for d in filter(lambda d: d[act_key] is not None, borders.groupby([act_key]).count().to_dicts()):
        dfg.end_activities[d[act_key]] = d['count']

    for d in df.filter((df[cid_key] == df[aux_case])).groupby([act_key, aux_act]).count().to_dicts():
        dfg.graph[(d[act_key], d[aux_act])] = d['count']

    return dfg

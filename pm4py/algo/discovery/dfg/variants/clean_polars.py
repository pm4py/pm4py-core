'''
PM4Py – A Process Mining Library for Python
Copyright (C) 2026 Process Intelligence Solutions GmbH

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see this software project's root or
visit <https://www.gnu.org/licenses/>.

Website: https://processintelligence.solutions
Contact: info@processintelligence.solutions
'''
import time
from enum import Enum
from typing import Optional, Dict, Any, Union

import polars as pl

from pm4py.objects.dfg.obj import DFG
from pm4py.util import constants, exec_utils
from pm4py.util import xes_constants as xes_util


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY


CONST_AUX_ACT = "aux_act_"
CONST_AUX_CASE = "aux_case_"
CONST_COUNT = "count_"


def apply(
    log: Union[pl.DataFrame, pl.LazyFrame], parameters: Optional[Dict[str, Any]] = None
) -> DFG:
    parameters = {} if parameters is None else parameters
    act_key = exec_utils.get_param_value(
        Parameters.ACTIVITY_KEY, parameters, xes_util.DEFAULT_NAME_KEY
    )
    cid_key = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, constants.CASE_ATTRIBUTE_GLUE
    )
    time_key = exec_utils.get_param_value(
        Parameters.TIMESTAMP_KEY, parameters, xes_util.DEFAULT_TIMESTAMP_KEY
    )
    aux_act = CONST_AUX_ACT + str(time.time())
    df = log.lazy() if isinstance(log, pl.DataFrame) else log
    df = df.select([cid_key, act_key, time_key]).sort(
        [cid_key, time_key], maintain_order=True
    )
    cases = df.group_by(cid_key).agg(
        pl.col(act_key).first().alias("__start_activity"),
        pl.col(act_key).last().alias("__end_activity"),
    )
    dfg = DFG()

    for column, counts in (
        ("__start_activity", dfg.start_activities),
        ("__end_activity", dfg.end_activities),
    ):
        activities = cases.group_by(column).len(name="count").collect()
        for activity, count in activities.iter_rows():
            if activity is not None:
                counts[activity] = count

    for d in (
        df.with_columns(pl.col(act_key).shift(-1).over(cid_key).alias(aux_act))
        .filter(pl.col(act_key).is_not_null() & pl.col(aux_act).is_not_null())
        .group_by([act_key, aux_act])
        .len(name="count")
        .collect()
        .to_dicts()
    ):
        dfg.graph[(d[act_key], d[aux_act])] = d["count"]

    return dfg

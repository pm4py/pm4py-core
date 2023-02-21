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

import pandas as pd

from enum import Enum
from typing import Optional, Dict, Any

from pm4py.util import constants
from pm4py.util import exec_utils
from pm4py.util import xes_constants, pandas_utils


class Parameters(Enum):
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    INDEX_KEY = "index_key"
    INDEX_IN_TRACE_KEY = "index_in_trace_key"
    USE_EXTREMES_TIMESTAMP = "use_extremes_timestamp"
    TEMP_COLUMN = "temp_column"
    FIRST_OR_LAST = "first_or_last"
    STRICT = "strict"


def apply(df: pd.DataFrame, activity: str, parameters: Optional[Dict[Any, Any]] = None):
    """
    Filter all the suffixes to a given activity (first or last occurrence of the activity in the case).

    Parameters
    ----------------
    df
        Dataframe
    parameters
        Parameters of the algorithm:
        - Parameters.CASE_ID_KEY => the case identifier column.
        - Parameters.ACTIVITY_KEY => the activity column.
        - Parameters.INDEX_IN_TRACE_KEY => attribute that should act as container of the index of the event inside
                                            the case.
        - Parameters.TEMP_COLUMN => temporary column which is used for internal purposes.
        - Parameters.FIRST_OR_LAST => filter on the first or last occurrence of an activity in the dataframe.
        - Parameters.STRICT => applies the filter in a strict (<) or lean (<=) way (boolean).

    Returns
    ----------------
    df
        Dataframe filtered keeping the prefixes to a given activity (first or last occurrence of the activity in the case).
    """
    if parameters is None:
        parameters = {}

    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    index_in_trace_key = exec_utils.get_param_value(Parameters.INDEX_IN_TRACE_KEY, parameters, constants.DEFAULT_INDEX_IN_TRACE_KEY)
    temp_column = exec_utils.get_param_value(Parameters.TEMP_COLUMN, parameters, "@@temp_column")
    first_or_last = exec_utils.get_param_value(Parameters.FIRST_OR_LAST, parameters, "first")
    strict = exec_utils.get_param_value(Parameters.STRICT, parameters, True)

    if index_in_trace_key not in df.columns:
        df = pandas_utils.insert_ev_in_tr_index(df, column_name=index_in_trace_key, case_id=case_id_key)

    position_activity = df[df[activity_key] == activity].groupby(case_id_key)
    if first_or_last == "first":
        position_activity = position_activity.first()
    elif first_or_last == "last":
        position_activity = position_activity.last()
    position_activity = position_activity.reset_index()[[case_id_key, index_in_trace_key]].to_dict("records")
    position_activity = {x[case_id_key]: x[index_in_trace_key] for x in position_activity}

    df[temp_column] = df[case_id_key].map(position_activity)
    if strict:
        df = df[df[index_in_trace_key] > df[temp_column]]
    else:
        df = df[df[index_in_trace_key] >= df[temp_column]]

    return df

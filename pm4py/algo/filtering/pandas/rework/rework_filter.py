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
from enum import Enum
from pm4py.util import constants, xes_constants, exec_utils, pandas_utils
from typing import Optional, Dict, Any
import pandas as pd
from copy import copy


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    MIN_OCCURRENCES = "min_occurrences"
    POSITIVE = "positive"


INT_CASE_ACT_SIZE = "@@int_case_act_size"


def apply(df0: pd.DataFrame, activity: str, parameters: Optional[Dict[Any, Any]] = None) -> pd.DataFrame:
    """
    Applies the rework filter on the provided dataframe and activity.
    This filter the cases of the log having at least Parameters.MIN_OCCURRENCES (default: 2) occurrences
    of the given activity.

    It is also possible (setting Parameters.POSITIVE to False) to retrieve the cases of the log not having the
    given activity or having the activity occurred less than Parameters.MIN_OCCURRENCES times.

    Parameters
    -------------------
    df0
        Dataframe
    activity
        Activity of which the rework shall be filtered
    parameters
        Parameters of the filter, including:
        - Parameters.ACTIVITY_KEY => the attribute to use as activity
        - Parameters.CASE_ID_KEY => the attribute to use as case ID
        - Parameters.MIN_OCCURRENCES => the minimum number of occurrences for the activity
        - Parameters.POSITIVE => if True, filters the cases of the log having at least MIN_OCCURRENCES occurrences.
            if False, filters the cases of the log where such behavior does not occur.

    Returns
    -----------------
    filtered_df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
    min_occurrences = exec_utils.get_param_value(Parameters.MIN_OCCURRENCES, parameters, 2)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)

    df = df0.copy()
    df = df[list({activity_key, case_id_key})]
    df = df[df[activity_key] == activity]
    df[INT_CASE_ACT_SIZE] = df.groupby([activity_key, case_id_key]).cumcount()
    cases = pandas_utils.format_unique(df[df[INT_CASE_ACT_SIZE] >= (min_occurrences-1)][case_id_key].unique())

    if positive:
        ret = df0[df0[case_id_key].isin(cases)]
    else:
        ret = df0[~df0[case_id_key].isin(cases)]

    ret.attrs = copy(df0.attrs) if hasattr(df0, 'attrs') else {}
    return ret

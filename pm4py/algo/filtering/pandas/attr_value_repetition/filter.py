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
import sys
from enum import Enum
from typing import Any, Optional, Dict, Union

import pandas as pd

from pm4py.util import constants, xes_constants, exec_utils
from copy import copy


class Parameters(Enum):
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    ATTRIBUTE_KEY = constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY
    MIN_REP = "min_rep"
    MAX_REP = "max_rep"


def apply(df: pd.DataFrame, value: Any, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> pd.DataFrame:
    """
    Filters the trace of the dataframe where the given attribute value is repeated
    (in a range of repetitions that is specified by the user)

    Parameters
    ----------------
    df
        Dataframe
    value
        Value that is investigated
    parameters
        Parameters of the filter, including:
        - Parameters.ATTRIBUTE_KEY => the attribute key
        - Parameters.MIN_REP => minimum number of repetitions
        - Parameters.MAX_REP => maximum number of repetitions
        - Parameters.CASE_ID_KEY => the columns of the dataframe that is the case identifier

    Returns
    ----------------
    filtered_df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}

    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
    attribute_key = exec_utils.get_param_value(Parameters.ATTRIBUTE_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    min_rep = exec_utils.get_param_value(Parameters.MIN_REP, parameters, 2)
    max_rep = exec_utils.get_param_value(Parameters.MAX_REP, parameters, sys.maxsize)

    filtered_df = df[df[attribute_key] == value]
    filtered_df = filtered_df.groupby(case_id_key).size().reset_index()
    filtered_df = filtered_df[filtered_df[0] >= min_rep]
    filtered_df = filtered_df[filtered_df[0] <= max_rep]

    ret = df[df[case_id_key].isin(filtered_df[case_id_key])]
    ret.attrs = copy(df.attrs) if hasattr(df, 'attrs') else {}
    return ret

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
from typing import Optional, Dict, Any, Union

import numpy as np
import pandas as pd

from pm4py.util import exec_utils, constants, xes_constants


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    SUBCASE_CONCAT_STR = "subcase_concat_str"


def apply(df: pd.DataFrame, act1: str, act2: str,
          parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> pd.DataFrame:
    """
    Given a dataframe, filters all the subtraces going from an event with activity "act1" to an event with
    activity "act2"

    Parameters
    ----------------
    df
        Dataframe
    act1
        First activity
    act2
        Second activity
    parameters
        Parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY => activity key
        - Parameters.CASE_ID_KEY => case id
        - Parameters.SUBCASE_CONCAT_STR => concatenator between the case id and the subtrace index in the filtered df

    Returns
    ----------------
    filtered_df
        Dataframe with all the subtraces going from "act1" to "act2"
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
    subcase_concat_str = exec_utils.get_param_value(Parameters.SUBCASE_CONCAT_STR, parameters, "##@@")

    df = df.copy()
    cases = df[case_id_key].to_numpy()
    activities = df[activity_key].to_numpy()
    c_unq, c_ind, c_counts = np.unique(cases, return_index=True, return_counts=True)
    res = [np.nan for i in range(len(df))]

    i = 0
    while i < len(c_unq):
        rel_count = 0
        occ_A = -1
        j = 0
        while j < c_counts[i]:
            if activities[c_ind[i] + j] == act2 and occ_A >= 0:
                z = occ_A
                this_case = str(c_unq[i]) + subcase_concat_str + str(rel_count)
                while z <= j:
                    res[c_ind[i] + z] = this_case
                    z = z + 1
                rel_count += 1
                occ_A = -1
            elif activities[c_ind[i] + j] == act1 and occ_A == -1:
                occ_A = j
            j = j + 1
        i = i + 1

    df[case_id_key] = res
    df = df.dropna(subset=[case_id_key])

    return df

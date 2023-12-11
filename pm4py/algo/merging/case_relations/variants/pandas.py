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
from pm4py.util import exec_utils, constants, xes_constants, pandas_utils
from enum import Enum
from typing import Optional, Dict, Any


class Parameters(Enum):
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    LEFT_SUFFIX = "left_suffix"
    RIGHT_SUFFIX = "right_suffix"


def apply(dataframe1: pd.DataFrame, dataframe2: pd.DataFrame, case_relations: pd.DataFrame,
          parameters: Optional[Dict[Any, Any]] = None) -> pd.DataFrame:
    """
    Merges the two dataframes (dataframe1 and dataframe2), inserting the events of the second
    dataframe inside the cases of the first dataframe.
    This is done using a background knowledge provided in the case_relations dataframe, where the cases of the two dataframes
    are put in relations.
    E.g., if in dataframe1 and dataframe2 there are two case ID columns (case:concept:name),
    they are put in relations by case_relations having two columns case:concept:name_LEFT and case:concept:name_RIGHT

    Parameters
    -----------------
    dataframe1
        Reference dataframe (in which the events of the other dataframe are inserted)
    dataframe2
        Second dataframe (to insert in the cases of the first)
    case_relations
        Case relations dataframe
    parameters
        Parameters of the algorithm, including:
        - Parameters.TIMESTAMP_KEY => the timestamp key to use (default: time:timestamp)
        - Parameters.CASE_ID_KEY => the case identifier to use (default: case:concept:name)
        - Parameters.LEFT_SUFFIX => the suffix to the case identifier column of the first dataframe
        - Parameters.RIGHT_SUFFIX => the suffix to the case identifier column of the second dataframe

    Returns
    ----------------
    merged_dataframe
        Merged dataframe
    """
    if parameters is None:
        parameters = {}

    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    left_suffix = exec_utils.get_param_value(Parameters.LEFT_SUFFIX, parameters, "_LEFT")
    right_suffix = exec_utils.get_param_value(Parameters.RIGHT_SUFFIX, parameters, "_RIGHT")
    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)

    dataframe2 = dataframe2.merge(case_relations, left_on=case_id_key, right_on=case_id_key + right_suffix)
    dataframe2[case_id_key] = dataframe2[case_id_key + left_suffix]

    dataframe1 = pandas_utils.concat([dataframe1, dataframe2])
    dataframe1 = dataframe1.sort_values([case_id_key, timestamp_key])

    return dataframe1

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
from typing import Optional, Dict, Any
from enum import Enum
from pm4py.util import exec_utils, constants, xes_constants, pandas_utils
from pm4py.objects.log.util import dataframe_utils
from copy import copy


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    LEFT_SUFFIX = "left_suffix"
    RIGHT_SUFFIX = "right_suffix"
    INDEX_KEY = "index_key"


def directly_follows_dataframe(dataframe: pd.DataFrame, parameters: Optional[Dict[Any, Any]] = None):
    """
    Calculates the directly-follows dataframe (internal usage)
    """
    if parameters is None:
        parameters = {}

    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)
    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
    index_key = exec_utils.get_param_value(Parameters.INDEX_KEY, parameters, constants.DEFAULT_INDEX_KEY)

    if not (hasattr(dataframe, "attrs") and dataframe.attrs):
        # dataframe has not been initialized through format_dataframe
        dataframe = pandas_utils.insert_index(dataframe, index_key)
        dataframe.sort_values([case_id_key, timestamp_key, index_key])

    dataframe = pandas_utils.insert_index(dataframe, index_key)

    insert_parameters = copy(parameters)
    insert_parameters["use_extremes_timestamp"] = True

    dataframe = dataframe_utils.insert_artificial_start_end(dataframe, parameters=insert_parameters)

    df_shifted = dataframe.shift(-1)
    df_shifted.columns = [x+"_2" for x in df_shifted.columns]
    dataframe = pandas_utils.concat([dataframe, df_shifted], axis=1)
    dataframe = dataframe[dataframe[case_id_key] == dataframe[case_id_key+"_2"]]

    return dataframe


def merge_dataframes(left_df: pd.DataFrame, right_df: pd.DataFrame, case_relations: pd.DataFrame, parameters: Optional[Dict[Any, Any]] = None):
    """
    Merge the two dataframes based on the provided case relations

    Parameters
    -----------------
    left_df
        First dataframe to merge
    right_df
        Second dataframe to merge
    case_relations
        Dictionary associating the cases of the first dataframe (column: case:concept:name_LEFT) to the
        cases of the second dataframe (column: case:concept:name_RIGHT)
    parameters
        Parameters of the algorithm, including:
        - Parameters.CASE_ID_KEY => the case ID
        - Parameters.LEFT_SUFFIX => the suffix for the columns of the left dataframe
        - Parameters.RIGHT_SUFFIX => the suffix for the columns of the right dataframe

    Returns
    ------------------
    merged_df
        Merged dataframe
    """
    if parameters is None:
        parameters = {}

    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
    left_suffix = exec_utils.get_param_value(Parameters.LEFT_SUFFIX, parameters, "_LEFT")
    right_suffix = exec_utils.get_param_value(Parameters.RIGHT_SUFFIX, parameters, "_RIGHT")

    left_df = directly_follows_dataframe(left_df, parameters=parameters)
    right_df = directly_follows_dataframe(right_df, parameters=parameters)

    left_df = left_df.merge(case_relations, left_on=case_id_key, right_on=case_id_key+left_suffix, suffixes=('', ''))
    del left_df[case_id_key+left_suffix]

    left_df = left_df.merge(right_df, left_on=case_id_key+right_suffix, right_on=case_id_key, suffixes=(left_suffix, right_suffix))

    return left_df

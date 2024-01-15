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
from pm4py.algo.discovery.ocel.interleavings.utils import merge_dataframe_rel_cases
import pandas as pd
from typing import Optional, Dict, Any
from pm4py.util import exec_utils, constants, xes_constants, pandas_utils
from enum import Enum


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    LEFT_SUFFIX = "left_suffix"
    RIGHT_SUFFIX = "right_suffix"
    INDEX_KEY = "index_key"
    SOURCE_ACTIVITY = "source_activity_param"
    TARGET_ACTIVITY = "target_activity_param"
    SOURCE_TIMESTAMP = "source_timestamp_param"
    TARGET_TIMESTAMP = "target_timestamp_param"
    LEFT_INDEX = "left_index_param"
    RIGHT_INDEX = "right_index_param"
    DIRECTION = "direction_param"
    TIMESTAMP_DIFF = "timestamp_diff"


def apply(left_df: pd.DataFrame, right_df: pd.DataFrame, case_relations: pd.DataFrame, parameters: Optional[Dict[Any, Any]] = None):
    """
    Calculates the timestamp-based interleavings ongoing from the left/right to the right/left dataframe.

    Parameters
    ------------------
    left_df
        Left dataframe
    right_df
        Right dataframe
    case_relations
        Dictionary associating the cases of the first dataframe (column: case:concept:name_LEFT) to the
        cases of the second dataframe (column: case:concept:name_RIGHT)
    parameters
        Parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY => the attribute to use as activity
        - Parameters.TIMESTAMP_KEY => the attribute to use as timestamp
        - Parameters.CASE_ID_KEY => the attribute to use as case identifier
        - Parameters.LEFT_SUFFIX => the suffix for the columns of the left dataframe
        - Parameters.RIGHT_SUFFIX => the suffix for the columns of the right dataframe
        - Parameters.INDEX_KEY => the index column in the dataframe
        - Parameters.SOURCE_ACTIVITY => the source activity of the interleaving
        - Parameters.TARGET_ACTIVITY => the target activity of the interleaving
        - Parameters.SOURCE_TIMESTAMP => the source timestamp of the interleaving
        - Parameters.TARGET_TIMESTAMP => the target timestamp of the interleaving
        - Parameters.LEFT_INDEX => the index of the event of the left-dataframe in the interleaving
        - Parameters.RIGHT_INDEX => the index of the event of the right-dataframe in the interleaving
        - Parameters.DIRECTION => the direction of the interleaving (LR: left to right; RL: right to left)
        - Parameters.TIMESTAMP_DIFF => the difference between the timestamps of the interleaving

    Returns
    -----------------
    interleavings_dataframe
        Sorted interleaving dataframe
    """
    if parameters is None:
        parameters = {}

    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)
    index_key = exec_utils.get_param_value(Parameters.INDEX_KEY, parameters, constants.DEFAULT_INDEX_KEY)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    left_suffix = exec_utils.get_param_value(Parameters.LEFT_SUFFIX, parameters, "_LEFT")
    right_suffix = exec_utils.get_param_value(Parameters.RIGHT_SUFFIX, parameters, "_RIGHT")
    source_activity = exec_utils.get_param_value(Parameters.SOURCE_ACTIVITY, parameters, "@@source_activity")
    target_activity = exec_utils.get_param_value(Parameters.TARGET_ACTIVITY, parameters, "@@target_activity")
    source_timestamp = exec_utils.get_param_value(Parameters.SOURCE_TIMESTAMP, parameters, "@@source_timestamp")
    target_timestamp = exec_utils.get_param_value(Parameters.TARGET_TIMESTAMP, parameters, "@@target_timestamp")
    direction = exec_utils.get_param_value(Parameters.DIRECTION, parameters, "@@direction")
    timestamp_diff = exec_utils.get_param_value(Parameters.TIMESTAMP_DIFF, parameters, "@@timestamp_diff")
    left_index = exec_utils.get_param_value(Parameters.LEFT_INDEX, parameters, "@@left_index")
    right_index = exec_utils.get_param_value(Parameters.RIGHT_INDEX, parameters, "@@right_index")

    md = merge_dataframe_rel_cases.merge_dataframes(left_df, right_df, case_relations, parameters=parameters)

    df1 = md[md[timestamp_key+left_suffix] < md[timestamp_key+right_suffix]]
    df1 = df1[df1[timestamp_key+right_suffix] < df1[timestamp_key+"_2"+left_suffix]]
    df1 = df1[df1[timestamp_key+"_2"+left_suffix] < df1[timestamp_key+"_2"+right_suffix]]
    df1[source_activity] = df1[activity_key+left_suffix]
    df1[target_activity] = df1[activity_key+right_suffix]
    df1[source_timestamp] = df1[timestamp_key+left_suffix]
    df1[target_timestamp] = df1[timestamp_key+right_suffix]
    df1[left_index] = df1[index_key+left_suffix]
    df1[right_index] = df1[index_key+right_suffix]
    df1[direction] = "LR"

    df2 = md[md[timestamp_key+right_suffix] < md[timestamp_key+left_suffix]]
    df2 = df2[df2[timestamp_key+left_suffix] < df2[timestamp_key+"_2"+right_suffix]]
    df2 = df2[df2[timestamp_key+"_2"+right_suffix] < df2[timestamp_key+"_2"+left_suffix]]
    df2[source_activity] = df2[activity_key+"_2"+right_suffix]
    df2[target_activity] = df2[activity_key+"_2"+left_suffix]
    df2[source_timestamp] = df2[timestamp_key+"_2"+right_suffix]
    df2[target_timestamp] = df2[timestamp_key+"_2"+left_suffix]
    df2[left_index] = df2[index_key+"_2"+left_suffix]
    df2[right_index] = df2[index_key+"_2"+right_suffix]
    df2[direction] = "RL"

    md = pandas_utils.concat([df1, df2])
    md = md.sort_values([index_key+left_suffix, index_key+right_suffix])
    md[timestamp_diff] = pandas_utils.get_total_seconds(md[target_timestamp] - md[source_timestamp])

    return md

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

from pm4py.util import exec_utils, pandas_utils, constants
from pm4py.util.constants import CASE_CONCEPT_NAME
from pm4py.util.constants import PARAMETER_CONSTANT_ATTRIBUTE_KEY, PARAMETER_CONSTANT_CASEID_KEY, \
    PARAMETER_CONSTANT_RESOURCE_KEY, PARAMETER_CONSTANT_TIMESTAMP_KEY
from pm4py.util.xes_constants import DEFAULT_NAME_KEY, DEFAULT_RESOURCE_KEY, DEFAULT_TIMESTAMP_KEY
from copy import copy
from typing import Optional, Dict, Any, Union, List
import pandas as pd


class Parameters(Enum):
    CASE_ID_KEY = PARAMETER_CONSTANT_CASEID_KEY
    ATTRIBUTE_KEY = PARAMETER_CONSTANT_ATTRIBUTE_KEY
    TIMESTAMP_KEY = PARAMETER_CONSTANT_TIMESTAMP_KEY
    RESOURCE_KEY = PARAMETER_CONSTANT_RESOURCE_KEY
    POSITIVE = "positive"
    ENABLE_TIMESTAMP = "enable_timestamp"
    TIMESTAMP_DIFF_BOUNDARIES = "timestamp_diff_boundaries"


POSITIVE = Parameters.POSITIVE
ENABLE_TIMESTAMP = Parameters.ENABLE_TIMESTAMP
TIMESTAMP_DIFF_BOUNDARIES = Parameters.TIMESTAMP_DIFF_BOUNDARIES


def eventually_follows(df0: pd.DataFrame, attribute_values: List[str], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> pd.DataFrame:
    """
    Applies the eventually follows rule

    Parameters
    ------------
    df0
        Dataframe
    attribute_values
        A list of attribute_values attribute_values[n] follows attribute_values[n-1] follows ... follows attribute_values[0]

    parameters
        Parameters of the algorithm, including the attribute key and the positive parameter:
        - If True, returns all the cases containing all attribute_values and in which attribute_values[i] was eventually followed by attribute_values[i + 1]
        - If False, returns all the cases not containing all attribute_values, or in which an instance of attribute_values[i] was not eventually
        followed by an instance of attribute_values[i + 1]

    Returns
    ------------
    filtered_df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME)
    attribute_key = exec_utils.get_param_value(Parameters.ATTRIBUTE_KEY, parameters, DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, DEFAULT_TIMESTAMP_KEY)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)
    timestamp_diff_boundaries = exec_utils.get_param_value(Parameters.TIMESTAMP_DIFF_BOUNDARIES, parameters, [])
    enable_timestamp = exec_utils.get_param_value(Parameters.ENABLE_TIMESTAMP, parameters, len(timestamp_diff_boundaries) > 0)

    colset = [case_id_glue, attribute_key]
    if enable_timestamp:
        colset.append(timestamp_key)

    df = df0.copy()
    df = df[colset]
    df = pandas_utils.insert_index(df)

    df_a = [df[df[attribute_key] == attribute_value].copy() for attribute_value in attribute_values]

    df_join = df_a[0].merge(df_a[1], on=case_id_glue, suffixes=('_0', "_1")).dropna()
    df_join[constants.DEFAULT_INDEX_KEY] = df_join[constants.DEFAULT_INDEX_KEY + "_0"]
    df_join["@@diffindex0"] = df_join[constants.DEFAULT_INDEX_KEY + "_1"] - df_join[constants.DEFAULT_INDEX_KEY + "_0"]
    df_join = df_join[df_join["@@diffindex0"] > 0]

    for i in range(2, len(df_a)):
        df_join = df_join.merge(df_a[i], on=case_id_glue, suffixes=('', "_%d" % i)).dropna()
        df_join["@@diffindex%d" % (i - 1)] = df_join[constants.DEFAULT_INDEX_KEY + "_%d" % i] - df_join[
            constants.DEFAULT_INDEX_KEY + "_%d" % (i - 1)]
        df_join = df_join[df_join["@@diffindex%d" % (i - 1)] > 0]

    if enable_timestamp:
        for i in range(1, len(df_a)):
            df_join["@@difftimestamp%d" % (i - 1)] = pandas_utils.get_total_seconds(df_join[timestamp_key + "_%d" % i] - df_join[timestamp_key + '_%d' % (i-1)])

            if timestamp_diff_boundaries:
                df_join = df_join[df_join["@@difftimestamp%d" % (i-1)] >= timestamp_diff_boundaries[i-1][0]]
                df_join = df_join[df_join["@@difftimestamp%d" % (i-1)] <= timestamp_diff_boundaries[i-1][1]]

    i1 = df.set_index(case_id_glue).index
    i2 = df_join.set_index(case_id_glue).index
    if positive:
        ret = df0[i1.isin(i2)]
    else:
        ret = df0[~i1.isin(i2)]

    ret.attrs = copy(df0.attrs) if hasattr(df0, 'attrs') else {}
    return ret


def A_next_B_next_C(df0: pd.DataFrame, A: str, B: str, C: str, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> pd.DataFrame:
    """
    Applies the A net B next C rule

    Parameters
    ------------
    df0
        Dataframe
    A
        A Attribute value
    B
        B Attribute value
    C
        C Attribute value
    parameters
        Parameters of the algorithm, including the attribute key and the positive parameter:
        - If True, returns all the cases containing A, B and C and in which A was directly followed by B and B was directly followed by C
        - If False, returns all the cases not containing A or B or C, or in which none instance of A was directly
        followed by an instance of B and B was directly followed by C

    Returns
    ------------
    filtered_df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME)
    attribute_key = exec_utils.get_param_value(Parameters.ATTRIBUTE_KEY, parameters, DEFAULT_NAME_KEY)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)

    df = df0.copy()
    df = df[[case_id_glue, attribute_key]]
    df = pandas_utils.insert_index(df)
    df_A = df[df[attribute_key] == A].copy()
    df_B = df[df[attribute_key] == B].copy()
    df_C = df[df[attribute_key] == C].copy()
    df_B["@@conceptname"] = df_B[case_id_glue]
    df_B = df_B.groupby(case_id_glue).last().set_index("@@conceptname")
    df_C["@@conceptname"] = df_C[case_id_glue]
    df_C = df_C.groupby(case_id_glue).last().set_index("@@conceptname")

    df_join = df_A.join(df_B, on=case_id_glue, rsuffix="_2").dropna().join(df_C, on=case_id_glue, rsuffix="_3").dropna()
    df_join["@@diffindex"] = df_join[constants.DEFAULT_INDEX_KEY + "_2"] - df_join[constants.DEFAULT_INDEX_KEY]
    df_join["@@diffindex2"] = df_join[constants.DEFAULT_INDEX_KEY + "_3"] - df_join[constants.DEFAULT_INDEX_KEY + "_2"]
    df_join = df_join[df_join["@@diffindex"] == 1]
    df_join = df_join[df_join["@@diffindex2"] == 1]

    i1 = df.set_index(case_id_glue).index
    i2 = df_join.set_index(case_id_glue).index

    if positive:
        ret = df0[i1.isin(i2)]
    else:
        ret = df0[~i1.isin(i2)]

    ret.attrs = copy(df0.attrs) if hasattr(df0, 'attrs') else {}
    return ret


def four_eyes_principle(df0: pd.DataFrame, A: str, B: str, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> pd.DataFrame:
    """
    Verifies the Four Eyes Principle given A and B

    Parameters
    -------------
    df0
        Dataframe
    A
        A attribute value
    B
        B attribute value
    parameters
        Parameters of the algorithm, including the attribute key and the positive parameter:
        - if True, then filters all the cases containing A and B which have empty intersection between the set
          of resources doing A and B
        - if False, then filters all the cases containing A and B which have no empty intersection between the set
          of resources doing A and B

    Returns
    --------------
    filtered_df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME)
    attribute_key = exec_utils.get_param_value(Parameters.ATTRIBUTE_KEY, parameters, DEFAULT_NAME_KEY)
    resource_key = exec_utils.get_param_value(Parameters.RESOURCE_KEY, parameters, DEFAULT_RESOURCE_KEY)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)

    df = df0.copy()
    df = df[[case_id_glue, attribute_key, resource_key]]

    df_A = df[df[attribute_key] == A].copy()
    df_B = df[df[attribute_key] == B].copy()
    df_B["@@conceptname"] = df_B[case_id_glue]
    df_B = df_B.groupby(case_id_glue).last().set_index("@@conceptname")

    df_join = df_A.join(df_B, on=case_id_glue, rsuffix="_2").dropna()
    df_join_pos = df_join[df_join[resource_key] == df_join[resource_key + "_2"]]
    df_join_neg = df_join[df_join[resource_key] != df_join[resource_key + "_2"]]

    i1 = df.set_index(case_id_glue).index
    i2 = df_join_pos.set_index(case_id_glue).index
    i3 = df_join_neg.set_index(case_id_glue).index

    if positive:
        ret = df0[i1.isin(i3) & ~i1.isin(i2)]
    else:
        ret = df0[i1.isin(i2)]

    ret.attrs = copy(df0.attrs) if hasattr(df0, 'attrs') else {}
    return ret


def attr_value_different_persons(df0: pd.DataFrame, A: str, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> pd.DataFrame:
    """
    Checks whether an attribute value is assumed on events done by different resources

    Parameters
    ------------
    df0
        Dataframe
    A
        A attribute value
    parameters
        Parameters of the algorithm, including the attribute key and the positive parameter:
            - if True, then filters all the cases containing occurrences of A done by different resources
            - if False, then filters all the cases not containing occurrences of A done by different resources

    Returns
    -------------
    filtered_df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME)
    attribute_key = exec_utils.get_param_value(Parameters.ATTRIBUTE_KEY, parameters, DEFAULT_NAME_KEY)
    resource_key = exec_utils.get_param_value(Parameters.RESOURCE_KEY, parameters, DEFAULT_RESOURCE_KEY)
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)

    df = df0.copy()
    df = df[[case_id_glue, attribute_key, resource_key]]

    df_A = df[df[attribute_key] == A].copy()
    df_B = df[df[attribute_key] == A].copy()
    df_B["@@conceptname"] = df_B[case_id_glue]
    df_B = df_B.groupby(case_id_glue).last().set_index("@@conceptname")

    df_join = df_A.join(df_B, on=case_id_glue, rsuffix="_2").dropna()
    df_join_neg = df_join[df_join[resource_key] != df_join[resource_key + "_2"]]

    i1 = df.set_index(case_id_glue).index
    i2 = df_join_neg.set_index(case_id_glue).index

    if positive:
        ret = df0[i1.isin(i2)]
    else:
        ret = df0[~i1.isin(i2)]

    ret.attrs = copy(df0.attrs) if hasattr(df0, 'attrs') else {}
    return ret

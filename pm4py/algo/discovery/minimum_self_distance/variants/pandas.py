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
from pm4py.util import exec_utils, constants, xes_constants, pandas_utils


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY


CONCAT_ACT_CASE = "@@concat_act_case"
INT_CASE_ACT_SIZE = "@@int_case_act_size"
DIFF_INDEX = "@@diff_index"


def apply(df, parameters=None):
    '''
    This algorithm computes the minimum self-distance for each activity observed in an event log.
    The self distance of a in <a> is infinity, of a in <a,a> is 0, in <a,b,a> is 1, etc.
    The minimum self distance is the minimal observed self distance value in the event log.
    The activity key needs to be specified in the parameters input object (if None, default value 'concept:name' is used).


    Parameters
    ----------
    df
        Pandas dataframe
    parameters
        parameters object;

    Returns
    -------
        dict mapping an activity to its self-distance, if it exists, otherwise it is not part of the dict.
    '''
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)

    df = df.copy()
    df = df[list({activity_key, case_id_key})]
    df = pandas_utils.insert_ev_in_tr_index(df, case_id=case_id_key, column_name=constants.DEFAULT_INDEX_IN_TRACE_KEY)
    df[CONCAT_ACT_CASE] = df[case_id_key] + df[activity_key]
    df[INT_CASE_ACT_SIZE] = df.groupby(CONCAT_ACT_CASE).cumcount()
    df_last = df.groupby(CONCAT_ACT_CASE).last().reset_index()
    df_last = df_last[df_last[INT_CASE_ACT_SIZE] > 0]
    df = df[df[CONCAT_ACT_CASE].isin(df_last[CONCAT_ACT_CASE])]
    df = df.merge(df, on=[activity_key, case_id_key], suffixes=('', '_2'))
    df[DIFF_INDEX] = df[constants.DEFAULT_INDEX_IN_TRACE_KEY+"_2"] - df[constants.DEFAULT_INDEX_IN_TRACE_KEY] - 1
    df = df[df[DIFF_INDEX] >= 0]
    ret = df.groupby(activity_key)[DIFF_INDEX].agg("min").to_dict()
    return ret

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

import numpy as np

from pm4py.util import constants, points_subset
from pm4py.util import exec_utils, pandas_utils
from pm4py.util import xes_constants as xes
from typing import Optional, Dict, Any, Union, List
import pandas as pd


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    PARAMETER_SAMPLE_SIZE = "sample_size"
    SORT_LOG_REQUIRED = "sort_log_required"


def gen_patterns(pattern, length):
    return ["".join(pattern[i:i + length]) for i in range(len(pattern) - (length - 1))]


def apply(dataframe: pd.DataFrame, list_activities: List[str], sample_size: int, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Dict[str, Any]:
    """
    Finds the disconnected performance spectrum provided a dataframe
    and a list of activities

    Parameters
    -------------
    dataframe
        Dataframe
    list_activities
        List of activities interesting for the performance spectrum (at least two)
    sample_size
        Size of the sample
    parameters
        Parameters of the algorithm,  including:
            - Parameters.ACTIVITY_KEY
            - Parameters.TIMESTAMP_KEY
            - Parameters.CASE_ID_KEY

    Returns
    -------------
    points
        Points of the performance spectrum
    """
    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes.DEFAULT_TIMESTAMP_KEY)

    sort_log_required = exec_utils.get_param_value(Parameters.SORT_LOG_REQUIRED, parameters, True)

    dataframe = dataframe[[case_id_glue, activity_key, timestamp_key]]
    dataframe = dataframe[dataframe[activity_key].isin(list_activities)]
    dataframe = pandas_utils.insert_index(dataframe, constants.DEFAULT_EVENT_INDEX_KEY)
    if sort_log_required:
        dataframe = dataframe.sort_values([case_id_glue, timestamp_key, constants.DEFAULT_EVENT_INDEX_KEY])
    dataframe[timestamp_key] = dataframe[timestamp_key].astype(np.int64) / 10 ** 9

    all_patterns = [(len(list_activities) - i, gen_patterns(list_activities, len(list_activities) - i)) for i in
                    range(len(list_activities) - 1)]

    def key(k, n):
        return k + str(n)

    def to_points(match, l):
        return {'case_id': match[key(case_id_glue, 0)],
                'points': [(match[key(activity_key, i)], match[key(timestamp_key, i)]) for i in range(l)]}

    points = []
    for l, patterns in all_patterns:
        # concat shifted and suffixed dataframes to get a dataframe that allows to check for the patterns
        dfs = [dataframe.add_suffix(str(i)).shift(-i) for i in range(l)]
        df_merged = pandas_utils.concat(dfs, axis=1)

        indices = [shift_index(dfs[i].index, i) for i in range(len(dfs))]
        mindex = pd.MultiIndex.from_arrays(indices)
        df_merged = df_merged.set_index(mindex)

        for i in range(l - 1):
            df_merged = df_merged[df_merged[key(case_id_glue, i)] == df_merged[key(case_id_glue, i + 1)]]

        column_list = [key(activity_key, i) for i in range(l)]
        matches = df_merged[np.isin(df_merged[column_list].sum(axis=1), patterns)]
        points.extend([to_points(m, l) for m in matches.to_dict('records')])
        # drop rows of this match to not discover subsets of this match again
        dataframe = dataframe.drop([int(i) for indices in matches.index for i in indices[:-1]])
        pass

    points = sorted(points, key=lambda x: min(x['points'], key=lambda x: x[1])[1])
    if len(points) > sample_size:
        points = points_subset.pick_chosen_points_list(sample_size, points)

    return points


def shift_index(index, n):
    if n == 0:
        return list(index)
    nones = [None for _ in range(n)]
    return list(index[n:]) + nones

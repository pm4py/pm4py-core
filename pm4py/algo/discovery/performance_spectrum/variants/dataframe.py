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

from pm4py.util import constants
from pm4py.util import exec_utils, pandas_utils
from pm4py.util import xes_constants as xes
from pm4py.util.constants import CASE_CONCEPT_NAME
from typing import Optional, Dict, Any, Union, List
import pandas as pd


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    ATTRIBUTE_KEY = constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY
    PARAMETER_SAMPLE_SIZE = "sample_size"
    SORT_LOG_REQUIRED = "sort_log_required"


def apply(dataframe: pd.DataFrame, list_activities: List[str], sample_size: int, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Dict[str, Any]:
    """
    Finds the performance spectrum provided a dataframe
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

    import pandas as pd
    import numpy as np

    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes.DEFAULT_TIMESTAMP_KEY)
    sort_log_required = exec_utils.get_param_value(Parameters.SORT_LOG_REQUIRED, parameters, True)

    dataframe = dataframe[[case_id_glue, activity_key, timestamp_key]]
    dataframe[activity_key] = dataframe[activity_key].astype("string")
    dataframe = dataframe[dataframe[activity_key].isin(list_activities)]
    dataframe = pandas_utils.insert_index(dataframe, constants.DEFAULT_EVENT_INDEX_KEY)
    if sort_log_required:
        dataframe = dataframe.sort_values([case_id_glue, timestamp_key, constants.DEFAULT_EVENT_INDEX_KEY])
    dataframe[timestamp_key] = dataframe[timestamp_key].astype(np.int64) / 10 ** 9

    def key(k, n):
        return k + str(n)

    # create a dataframe with all needed columns to check for the activities pattern 
    dfs = [dataframe.add_suffix(str(i)).shift(-i) for i in range(len(list_activities))]
    dataframe = pandas_utils.concat(dfs, axis=1)
    # keep only rows that belong to exactly one case
    for i in range(len(list_activities) - 1):
        dataframe = dataframe[dataframe[key(case_id_glue, i)] == dataframe[key(case_id_glue, i + 1)]]

    column_list = [key(activity_key, i) for i in range(len(list_activities))]
    pattern = "".join(list_activities)
    # keep only rows that have the desired activities pattern

    matches = dataframe[np.equal(dataframe[column_list].agg(''.join, axis=1), pattern)]
    if len(matches) > sample_size:
        matches = matches.sample(n=sample_size)

    filt_col_names = [timestamp_key + str(i) for i in range(len(list_activities))]
    points = pandas_utils.to_dict_records(matches)
    points = [[p[tk] for tk in filt_col_names] for p in points]
    points = sorted(points, key=lambda x: x[0])

    return points

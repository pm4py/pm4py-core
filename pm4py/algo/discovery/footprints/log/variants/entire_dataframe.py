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
from pm4py.util import xes_constants
from pm4py.util import constants
from pm4py.algo.discovery.dfg.adapters.pandas import df_statistics
from pm4py.util import exec_utils, pandas_utils
from pm4py.algo.discovery.causal import algorithm as causal_discovery
from enum import Enum
from typing import Optional, Dict, Any, Union
import pandas as pd


class Outputs(Enum):
    DFG = "dfg"
    SEQUENCE = "sequence"
    PARALLEL = "parallel"
    START_ACTIVITIES = "start_activities"
    END_ACTIVITIES = "end_activities"
    ACTIVITIES = "activities"
    SKIPPABLE = "skippable"
    ACTIVITIES_ALWAYS_HAPPENING = "activities_always_happening"
    MIN_TRACE_LENGTH = "min_trace_length"
    TRACE = "trace"


class Parameters(Enum):
    SORT_REQUIRED = "sort_required"
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    INDEX_KEY = "index_key"


DEFAULT_SORT_REQUIRED = True
DEFAULT_INDEX_KEY = "@@index"


def apply(df: pd.DataFrame, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Dict[str, Any]:
    """
    Discovers a footprint object from a dataframe
    (the footprints of the dataframe are returned)

    Parameters
    --------------
    df
        Dataframe
    parameters
        Parameters of the algorithm

    Returns
    --------------
    footprints_obj
        Footprints object
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    caseid_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
    start_timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               None)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    sort_required = exec_utils.get_param_value(Parameters.SORT_REQUIRED, parameters, DEFAULT_SORT_REQUIRED)
    index_key = exec_utils.get_param_value(Parameters.INDEX_KEY, parameters, DEFAULT_INDEX_KEY)

    df = df[[caseid_key, activity_key, timestamp_key]]
    if sort_required:
        df = pandas_utils.insert_index(df, index_key)
        if start_timestamp_key is not None:
            df = df.sort_values([caseid_key, start_timestamp_key, timestamp_key, index_key])
        else:
            df = df.sort_values([caseid_key, timestamp_key, index_key])

    grouped_df = df.groupby(caseid_key)
    dfg = df_statistics.get_dfg_graph(df, measure="frequency", activity_key=activity_key, case_id_glue=caseid_key,
                                      timestamp_key=timestamp_key, sort_caseid_required=False,
                                      sort_timestamp_along_case_id=False, start_timestamp_key=start_timestamp_key)
    activities = set(pandas_utils.format_unique(df[activity_key].unique()))
    start_activities = set(pandas_utils.format_unique(grouped_df.first()[activity_key].unique()))
    end_activities = set(pandas_utils.format_unique(grouped_df.last()[activity_key].unique()))

    parallel = {(x, y) for (x, y) in dfg if (y, x) in dfg}
    sequence = set(causal_discovery.apply(dfg, causal_discovery.Variants.CAUSAL_ALPHA))

    ret = {}
    ret[Outputs.DFG.value] = dfg
    ret[Outputs.SEQUENCE.value] = sequence
    ret[Outputs.PARALLEL.value] = parallel
    ret[Outputs.ACTIVITIES.value] = activities
    ret[Outputs.START_ACTIVITIES.value] = start_activities
    ret[Outputs.END_ACTIVITIES.value] = end_activities
    ret[Outputs.MIN_TRACE_LENGTH.value] = int(grouped_df.size().min())

    return ret

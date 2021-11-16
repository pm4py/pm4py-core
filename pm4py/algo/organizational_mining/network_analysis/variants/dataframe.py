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
from pm4py.util import exec_utils
from pm4py.util import xes_constants, constants, pandas_utils
import pandas as pd
from typing import Dict, Optional, Any, Tuple
from pm4py.util.business_hours import soj_time_business_hours_diff


class Parameters(Enum):
    SORTING_COLUMN = "sorting_column"
    INDEX_KEY = "index_key"
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    IN_COLUMN = "in_column"
    OUT_COLUMN = "out_column"
    NODE_COLUMN = "node_column"
    EDGE_COLUMN = "edge_column"
    INCLUDE_PERFORMANCE = "include_performance"
    BUSINESS_HOURS = "business_hours"
    WORKTIMING = "worktiming"
    WEEKENDS = "weekends"
    TIMESTAMP_DIFF_COLUMN = "timestamp_diff_column"


def apply(dataframe: pd.DataFrame, parameters: Optional[Dict[Any, Any]] = None) -> Dict[
    Tuple[str, str], Dict[str, Any]]:
    """
    Performs the network analysis on the provided dataframe

    Parameters
    -----------------
    dataframe
        Dataframe
    parameters
        Parameters of the algorithm, including:
        - Parameters.SORTING_COLUMN => the column that should be used to sort the log
        - Parameters.INDEX_KEY => the name for the index attribute in the log (inserted during the execution)
        - Parameters.TIMESTAMP_COLUMN => the timestamp column
        - Parameters.IN_COLUMN => the target column of the link (default: the case identifier; events of the same case are linked)
        - Parameters.OUT_COLUMN => the source column of the link (default: the case identifier; events of the same case are linked)
        - Parameters.NODE_COLUMN => the attribute to be used for the node definition (default: the resource of the log, org:resource)
        - Parameters.EDGE_COLUMN => the attribute (of the source event) to be used for the edge definition (default: the activity of the log, concept:name)
        - Parameters.INCLUDE_PERFORMANCE => considers the performance of the edge
        - Parameters.BUSINESS_HOURS => boolean value that enables the business hours
        - Parameters.WORKTIMING => defines the worktiming of the organization (e.g. [7, 17]) if business hours are enabled
        - Parameters.WEEKENDS => defines the weekends of the organization (e.g. [6, 7]) if business hours are enabled
        - Parameters.TIMESTAMP_DIFF_COLUMN => timestamp diff column

    Returns
    -----------------
    network_analysis
        Edges of the network analysis (first key: edge; second key: type; value: number of occurrences)
    """
    if parameters is None:
        parameters = {}

    sorting_column = exec_utils.get_param_value(Parameters.SORTING_COLUMN, parameters,
                                                xes_constants.DEFAULT_TIMESTAMP_KEY)
    index_key = exec_utils.get_param_value(Parameters.INDEX_KEY, parameters, constants.DEFAULT_INDEX_KEY)
    timestamp_column = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                                  xes_constants.DEFAULT_TIMESTAMP_KEY)
    in_column = exec_utils.get_param_value(Parameters.IN_COLUMN, parameters, constants.CASE_CONCEPT_NAME)
    out_column = exec_utils.get_param_value(Parameters.OUT_COLUMN, parameters, constants.CASE_CONCEPT_NAME)
    node_column = exec_utils.get_param_value(Parameters.NODE_COLUMN, parameters, xes_constants.DEFAULT_RESOURCE_KEY)
    edge_column = exec_utils.get_param_value(Parameters.EDGE_COLUMN, parameters, xes_constants.DEFAULT_NAME_KEY)
    include_performance = exec_utils.get_param_value(Parameters.INCLUDE_PERFORMANCE, parameters, False)
    business_hours = exec_utils.get_param_value(Parameters.BUSINESS_HOURS, parameters, False)
    worktiming = exec_utils.get_param_value(Parameters.WORKTIMING, parameters, [7, 17])
    weekends = exec_utils.get_param_value(Parameters.WEEKENDS, parameters, [6, 7])
    timestamp_diff_column = exec_utils.get_param_value(Parameters.TIMESTAMP_DIFF_COLUMN, parameters, "@@timestamp_diff")

    dataframe = dataframe[{timestamp_column, in_column, out_column, node_column, edge_column, sorting_column}]
    dataframe = dataframe.sort_values(sorting_column)
    dataframe = pandas_utils.insert_index(dataframe, index_key)

    edges = {}

    df_out = dataframe[[index_key, out_column, node_column, edge_column, timestamp_column]].dropna(
        subset=[out_column, node_column, edge_column, timestamp_column], how="any")
    df_out.columns = [x + "_out" for x in df_out.columns]
    df_in = dataframe[[index_key, in_column, node_column, timestamp_column]].dropna(
        subset=[in_column, node_column, timestamp_column], how="any")
    df_in.columns = [x + "_in" for x in df_in.columns]

    merged_df = df_out.merge(df_in, left_on=out_column + "_out", right_on=in_column + "_in")
    merged_df = merged_df[merged_df[index_key + "_in"] > merged_df[index_key + "_out"]]
    merged_df = merged_df.groupby([index_key + "_out", out_column + "_out", in_column + "_in"]).first().reset_index()

    if business_hours:
        merged_df[timestamp_diff_column] = merged_df.apply(
            lambda x: soj_time_business_hours_diff(x[timestamp_column + "_out"], x[timestamp_column + "_in"],
                                                   worktiming,
                                                   weekends), axis=1)

    else:
        merged_df[timestamp_diff_column] = (
                merged_df[timestamp_column + "_in"] - merged_df[timestamp_column + "_out"]).astype(
            'timedelta64[s]')

    edges0 = merged_df.groupby([node_column + "_out", node_column + "_in", edge_column + "_out"])[
        timestamp_diff_column].apply(list).to_dict()

    for e0 in edges0:
        edge = (e0[0], e0[1])
        edge_value = e0[2]
        if edge not in edges:
            edges[edge] = {}
        if edge_value not in edges[edge]:
            if include_performance:
                edges[edge][edge_value] = edges0[e0]
            else:
                edges[edge][edge_value] = len(edges0[e0])

    return edges

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
from typing import Optional, Dict, Any, Set
import pandas as pd


class Parameters(Enum):
    OUT_COLUMN = "out_column"
    IN_COLUMN = "in_column"
    SORTING_COLUMN = "sorting_column"
    INDEX_COLUMN = "index_column"
    LOOK_FORWARD = "look_forward"
    KEEP_FIRST_OCCURRENCE = "keep_first_occurrence"
    PROPAGATE = "propagate"


def propagate_associations(associations: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
    """
    Propagate the associations, such that the eventually-follows
    flow between the events of the event log is considered

    Parameters
    -------------------
    associations
        Associations between events

    Returns
    ------------------
    propagated_associations
        Propagated associations
    """
    reverse_dict = {}
    for x in associations:
        for k in associations[x]:
            if k not in reverse_dict:
                reverse_dict[k] = set()
            reverse_dict[k].add(x)
    change_dict = {x: True for x in associations}
    to_change = [x for x in change_dict if change_dict[x]]
    while to_change:
        for x in to_change:
            change_dict[x] = False
        for x in to_change:
            if x in reverse_dict:
                rv = reverse_dict[x]
                for k in rv:
                    new_set = associations[k].union(associations[x])
                    if len(new_set) > len(associations[k]):
                        change_dict[k] = True
                        associations[k] = new_set
        to_change = [x for x in change_dict if change_dict[x]]
    return associations


def apply(dataframe: pd.DataFrame, parameters: Optional[Dict[Any, Any]] = None) -> pd.DataFrame:
    """
    Performs a link analysis between the entries of the current dataframe.
    The link analysis permits advanced filtering based on events connected in an
    output-input relation (e.g., the OUT column of the first is equal to the IN column
    of the second).

    When OUT_COLUMN = IN_COLUMN = CASE ID, it can be equivalent to the directly-follows graph
    (when Parameters.KEEP_FIRST_OCCURRENCE = True), and to the eventually-follows graph
    (when Parameters.KEEP_FIRST_OCCURRENCE = False).

    Parameters
    -----------------
    dataframe
        Pandas dataframe
    parameters
        Parameters of the algorithm, including:
        - Parameters.OUT_COLUMN => the output column of the dataframe
        - Parameters.IN_COLUMN => the input column of the dataframe
        - Parameters.SORTING_COLUMN => the column on top of which the
        - Parameters.INDEX_COLUMN => the attribute to use for the indexing
        - Parameters.LOOK_FORWARD => filters the relations in which the second event has an index >= than the index
        of the first event.
        - Parameters.KEEP_FIRST_OCCURRENCE => keep, for every source event, only the first-occurring relationship
        with a target event (OUT=IN).
        - Parameters.PROPAGATE => propagate the relationships between events, in such a way that the entire document
        flow chain can be reconstructed.

    Returns
    -----------------
    link_analysis_dataframe
        Link analysis dataframe
    """
    if parameters is None:
        parameters = {}

    out_column = exec_utils.get_param_value(Parameters.OUT_COLUMN, parameters, constants.CASE_CONCEPT_NAME)
    in_column = exec_utils.get_param_value(Parameters.IN_COLUMN, parameters, constants.CASE_CONCEPT_NAME)
    sorting_column = exec_utils.get_param_value(Parameters.SORTING_COLUMN, parameters,
                                                xes_constants.DEFAULT_TIMESTAMP_KEY)
    index_column = exec_utils.get_param_value(Parameters.INDEX_COLUMN, parameters, constants.DEFAULT_INDEX_KEY)
    look_forward = exec_utils.get_param_value(Parameters.LOOK_FORWARD, parameters, True)
    keep_first_occurrence = exec_utils.get_param_value(Parameters.KEEP_FIRST_OCCURRENCE, parameters, False)
    propagate = exec_utils.get_param_value(Parameters.PROPAGATE, parameters, False)

    dataframe = dataframe.sort_values(sorting_column)
    dataframe = pandas_utils.insert_index(dataframe, index_column)

    df_red1 = dataframe[[out_column, index_column]]
    df_red2 = dataframe[[in_column, index_column]]
    df_red = df_red1.merge(df_red2, left_on=out_column, right_on=in_column, suffixes=("_out", "_in"))

    if look_forward:
        df_red = df_red[df_red[index_column + "_out"] < df_red[index_column + "_in"]]

    if keep_first_occurrence:
        df_red = df_red.groupby(index_column + "_out").first().reset_index()

    stream_red = df_red.to_dict("records")
    associations = {}
    for el in stream_red:
        if not el[index_column + "_out"] in associations:
            associations[el[index_column + "_out"]] = set()
        associations[el[index_column + "_out"]].add(el[index_column + "_in"])

    if propagate:
        associations = propagate_associations(associations)

    out_clmn = []
    in_clmn = []
    for k in associations:
        for v in associations[k]:
            out_clmn.append(k)
            in_clmn.append(v)

    rel = pandas_utils.instantiate_dataframe({index_column + "_out": out_clmn, index_column + "_in": in_clmn})

    df_link = dataframe.copy()
    df_link.columns = [x + "_out" for x in df_link.columns]
    df_link = df_link.merge(rel, left_on=index_column + "_out", right_on=index_column + "_out")
    dataframe.columns = [x + "_in" for x in dataframe.columns]
    df_link = df_link.merge(dataframe, left_on=index_column + "_in", right_on=index_column + "_in")

    return df_link

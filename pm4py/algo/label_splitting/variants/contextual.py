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
from typing import Optional, Dict, Any, Union, List
from pm4py.objects.log.obj import EventLog, EventStream
from pm4py.objects.conversion.log import converter as log_converter
import pandas as pd
from enum import Enum
from pm4py.util import constants, xes_constants, exec_utils, pandas_utils, nx_utils
from pm4py.util import regex, string_distance


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    INDEX_KEY = "index_key"
    TARGET_COLUMN = "target_column"
    ACTIVITIES_SUFFIX = "activities_suffix"
    TARGET_ACTIVITIES = "target_activities"
    PREFIX_LENGTH = "prefix_length"
    SUFFIX_LENGTH = "suffix_length"
    MIN_EDGE_WEIGHT = "min_edge_weight"


def __get_tuple_char_mapping(tup: List[str], sharobj: regex.SharedObj):
    """
    Maps every string in a tuple to a different character
    """
    ret = []
    for i in range(len(tup)):
        if tup[i] not in sharobj.mapping_dictio:
            regex.get_new_char(tup[i], sharobj)

        ret.append(sharobj.mapping_dictio[tup[i]])

    return "".join(ret)


def __normalized_edit_distance(s1: str, s2: str) -> float:
    """
    Computes the normalized edit distance between the two provided strings (0 to 1)
    """
    ned = 0
    if len(s1) > 0 or len(s2) > 0:
        ed = string_distance.levenshtein(s1, s2)
        ned = ed / max(len(s1), len(s2))
    return ned


def apply(log: Union[EventLog, EventStream, pd.DataFrame], parameters: Optional[Dict[Any, Any]] = None) -> pd.DataFrame:
    """
    Applies the technique of contextual label-splitting, to distinguish between different meanings of the same
    activity. The result is a Pandas dataframe where the contextual label-splitting has been applied.

    Reference paper:
    van Zelst, Sebastiaan J., et al. "Context-Based Activity Label-Splitting." International Conference on Business Process Management. Cham: Springer Nature Switzerland, 2023.

    Minimum Viable Example:

        import pm4py
        from pm4py.algo.label_splitting import algorithm as label_splitter

        log = pm4py.read_xes("tests/input_data/receipt.xes")
        log2 = label_splitter.apply(log, variant=label_splitter.Variants.CONTEXTUAL)


    Parameters
    ---------------
    log
        Event log
    parameters
        Possible parameters of the algorithm, including:
        - Parameters.PREFIX_LENGTH => the length of the prefix to consider in the context
        - Parameters.SUFFIX_LENGTH => the length of the suffix to consider in the context
        - Parameters.MIN_EDGE_WEIGHT => the minimum weight for an edge to be included in the segments graph
        - Parameters.TARGET_ACTIVITIES => the activities which should be targeted by the relabeling (default: all)
        - Parameters.TARGET_COLUMN => the column that should contain the re-labeled activity

    Returns
    ---------------
    dataframe
        Pandas dataframe with the re-labeling
    """
    if parameters is None:
        parameters = {}

    index_key = exec_utils.get_param_value(Parameters.INDEX_KEY, parameters, constants.DEFAULT_INDEX_KEY)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
    target_column = exec_utils.get_param_value(Parameters.TARGET_COLUMN, parameters, xes_constants.DEFAULT_NAME_KEY)
    activities_suffix = exec_utils.get_param_value(Parameters.ACTIVITIES_SUFFIX, parameters, "_")

    target_activities = exec_utils.get_param_value(Parameters.TARGET_ACTIVITIES, parameters, None)

    prefix_length = exec_utils.get_param_value(Parameters.PREFIX_LENGTH, parameters, 2)
    suffix_length = exec_utils.get_param_value(Parameters.SUFFIX_LENGTH, parameters, 2)
    min_edge_weight = exec_utils.get_param_value(Parameters.MIN_EDGE_WEIGHT, parameters, 0.0)

    sharobj = regex.SharedObj()
    log = log_converter.apply(log, variant=log_converter.Variants.TO_DATA_FRAME, parameters=parameters)
    if index_key not in log:
        log = pandas_utils.insert_index(log, index_key)

    gdf = log.groupby(case_id_key, sort=False)
    output = gdf[[activity_key, index_key]].agg(list).to_dict()
    cases = list(output[activity_key].keys())

    # STEP 0 : transform the event log into two lists
    # - the one containing the activities executed for each case
    # - the second one containing the indexes (positions) of the single events in the log
    activities = output[activity_key]
    activities = [activities[c] for c in cases]
    indexes = output[index_key]
    indexes = [indexes[c] for c in cases]

    # keep as baseline mapping (if remapping does not apply)
    # the original activity.
    final_mapping = {}
    for i in range(len(indexes)):
        for j in range(len(indexes[i])):
            final_mapping[indexes[i][j]] = activities[i][j]
            pass

    dict_segments_indexes = {}
    segments_chars_mapping = {}
    dict_segments_clustering = {}

    # keep some internal dictionaries.
    # in particular, 'dict_segments_indexes' maps every activity to some corresponding segments (prefix+suffix).
    # each prefix is mapped to the set of indexes (of the events) of the log for which the prefix applies.
    for i in range(len(activities)):
        for j in range(len(activities[i])):
            segment = (activities[i][j], tuple(activities[i][max(0, j - prefix_length):j] + activities[i][j + 1:min(
                len(activities[i]), j + suffix_length + 1)]))
            if activities[i][j] not in dict_segments_indexes:
                dict_segments_indexes[activities[i][j]] = {}
            if segment not in dict_segments_indexes[activities[i][j]]:
                dict_segments_indexes[activities[i][j]][segment] = set()
            if segment[1] not in segments_chars_mapping:
                segments_chars_mapping[segment[1]] = __get_tuple_char_mapping(segment[1], sharobj)
            dict_segments_indexes[activities[i][j]][segment].add(indexes[i][j])

    G = nx_utils.Graph()

    # STEP 1
    # creates the activity graph measuring the normalized edit-distance between every couple of segments related
    # to the same activity. if the weight of the connection is greater than a given amount (by default 0.0)
    # the corresponding connection is added to the graph
    for act in dict_segments_indexes:
        if target_activities is None or act in target_activities:
            for segment in dict_segments_indexes[act]:
                G.add_node(segment)

            for segment in dict_segments_indexes[act]:
                map_seg = segments_chars_mapping[segment[1]]
                for segment2 in dict_segments_indexes[act]:
                    if segment != segment2:
                        map_seg2 = segments_chars_mapping[segment2[1]]

                        weight = 1 - __normalized_edit_distance(map_seg, map_seg2)
                        if weight > min_edge_weight:
                            G.add_edge(segment, segment2, weight=weight)

    # STEP 2
    # applies modularity maximization clustering and stores the results
    if G.edges:
        communities = nx_utils.greedy_modularity_communities(G, weight="weight")
    else:
        # when the graph contains no edges, avoid to apply clustering, instead
        # consider each node as standalone
        nodes = list(G.nodes)
        communities = [[nodes[i]] for i in range(len(nodes))]

    for i, comm in enumerate(communities):
        comm = list(comm)
        act = comm[0][0]
        comm = [x for y in comm for x in dict_segments_indexes[act][y]]

        if act not in dict_segments_clustering:
            dict_segments_clustering[act] = []

        dict_segments_clustering[act].append([i, comm])

    # STEP 3
    # set-up the re-labeling if needed
    for act in dict_segments_clustering:
        dict_segments_clustering[act] = sorted(dict_segments_clustering[act], key=lambda x: (len(x[1]), x[0]), reverse=True)

        if len(dict_segments_clustering[act]) > 1:
            #print(act, "remapped")

            for i in range(len(dict_segments_clustering[act])):
                for x in dict_segments_clustering[act][i][1]:
                    final_mapping[x] = act + activities_suffix + str(i)

    # STEP 4
    # eventually, the relabeling applies
    log[target_column] = log[index_key].map(final_mapping)

    return log

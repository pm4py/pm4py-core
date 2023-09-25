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
from copy import deepcopy
from enum import Enum

from pm4py.algo.discovery.dfg import algorithm as dfg_alg
from pm4py.algo.filtering.dfg.dfg_filtering import clean_dfg_based_on_noise_thresh
from pm4py.objects.conversion.heuristics_net import converter as hn_conv_alg
from pm4py.objects.heuristics_net import defaults
from pm4py.objects.heuristics_net.node import Node
from pm4py.statistics.attributes.log import get as log_attributes
from pm4py.statistics.end_activities.log import get as log_ea_filter
from pm4py.statistics.start_activities.log import get as log_sa_filter
from pm4py.util import constants
from pm4py.util import exec_utils
from pm4py.util import xes_constants as xes
from typing import Optional, Dict, Any, Union, Tuple
from pm4py.objects.log.obj import EventLog
from pm4py.objects.petri_net.obj import PetriNet, Marking
import pandas as pd
from pm4py.objects.heuristics_net.obj import HeuristicsNet


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    DEPENDENCY_THRESH = "dependency_thresh"
    AND_MEASURE_THRESH = "and_measure_thresh"
    MIN_ACT_COUNT = "min_act_count"
    MIN_DFG_OCCURRENCES = "min_dfg_occurrences"
    DFG_PRE_CLEANING_NOISE_THRESH = "dfg_pre_cleaning_noise_thresh"
    LOOP_LENGTH_TWO_THRESH = "loop_length_two_thresh"
    HEU_NET_DECORATION = "heu_net_decoration"


def apply(log: EventLog, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Tuple[PetriNet, Marking, Marking]:
    """
    Discovers a Petri net using Heuristics Miner

    Parameters
    ------------
    log
        Event log
    parameters
        Possible parameters of the algorithm,
        including:
            - Parameters.ACTIVITY_KEY
            - Parameters.TIMESTAMP_KEY
            - Parameters.CASE_ID_KEY
            - Parameters.DEPENDENCY_THRESH
            - Parameters.AND_MEASURE_THRESH
            - Parameters.MIN_ACT_COUNT
            - Parameters.MIN_DFG_OCCURRENCES
            - Parameters.DFG_PRE_CLEANING_NOISE_THRESH
            - Parameters.LOOP_LENGTH_TWO_THRESH

    Returns
    ------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    """
    if parameters is None:
        parameters = {}

    heu_net = apply_heu(log, parameters=parameters)
    net, im, fm = hn_conv_alg.apply(heu_net, parameters=parameters)

    return net, im, fm


def apply_pandas(df: pd.DataFrame, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Tuple[PetriNet, Marking, Marking]:
    """
    Discovers a Petri net using Heuristics Miner

    Parameters
    ------------
    df
        Pandas dataframe
    parameters
        Possible parameters of the algorithm,
        including: activity_key, case_id_glue, timestamp_key,
        dependency_thresh, and_measure_thresh, min_act_count, min_dfg_occurrences, dfg_pre_cleaning_noise_thresh,
        loops_length_two_thresh

    Returns
    ------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    """
    if parameters is None:
        parameters = {}

    heu_net = apply_heu_pandas(df, parameters=parameters)

    return hn_conv_alg.apply(heu_net, parameters=parameters)


def apply_dfg(dfg: Dict[Tuple[str, str], int], activities=None, activities_occurrences=None, start_activities=None, end_activities=None,
              parameters: Optional[Dict[Any, Any]] = None) -> Tuple[PetriNet, Marking, Marking]:
    """
    Discovers a Petri net using Heuristics Miner

    Parameters
    ------------
    dfg
        Directly-Follows Graph
    activities
        (If provided) list of activities of the log
    activities_occurrences
        (If provided) dictionary of activities occurrences
    start_activities
        (If provided) dictionary of start activities occurrences
    end_activities
        (If provided) dictionary of end activities occurrences
    parameters
        Possible parameters of the algorithm,
        including:
            - Parameters.ACTIVITY_KEY
            - Parameters.TIMESTAMP_KEY
            - Parameters.CASE_ID_KEY
            - Parameters.DEPENDENCY_THRESH
            - Parameters.AND_MEASURE_THRESH
            - Parameters.MIN_ACT_COUNT
            - Parameters.MIN_DFG_OCCURRENCES
            - Parameters.DFG_PRE_CLEANING_NOISE_THRESH
            - Parameters.LOOP_LENGTH_TWO_THRESH

    Returns
    ------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    """
    if parameters is None:
        parameters = {}

    heu_net = apply_heu_dfg(dfg, activities=activities, activities_occurrences=activities_occurrences,
                            start_activities=start_activities, end_activities=end_activities, parameters=parameters)
    net, im, fm = hn_conv_alg.apply(heu_net, parameters=parameters)

    return net, im, fm


def apply_heu(log: EventLog, parameters: Optional[Dict[Any, Any]] = None) -> HeuristicsNet:
    """
    Discovers an Heuristics Net using Heuristics Miner

    Parameters
    ------------
    log
        Event log
    parameters
        Possible parameters of the algorithm,
        including:
            - Parameters.ACTIVITY_KEY
            - Parameters.TIMESTAMP_KEY
            - Parameters.CASE_ID_KEY
            - Parameters.DEPENDENCY_THRESH
            - Parameters.AND_MEASURE_THRESH
            - Parameters.MIN_ACT_COUNT
            - Parameters.MIN_DFG_OCCURRENCES
            - Parameters.DFG_PRE_CLEANING_NOISE_THRESH
            - Parameters.LOOP_LENGTH_TWO_THRESH

    Returns
    ------------
    heu
        Heuristics Net
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes.DEFAULT_NAME_KEY)
    heu_net_decoration = exec_utils.get_param_value(Parameters.HEU_NET_DECORATION, parameters, "frequency")

    start_activities = log_sa_filter.get_start_activities(log, parameters=parameters)
    end_activities = log_ea_filter.get_end_activities(log, parameters=parameters)
    activities_occurrences = log_attributes.get_attribute_values(log, activity_key, parameters=parameters)
    activities = list(activities_occurrences.keys())
    dfg = dfg_alg.apply(log, parameters=parameters)
    parameters_w2 = deepcopy(parameters)
    parameters_w2["window"] = 2
    dfg_window_2 = dfg_alg.apply(log, parameters=parameters_w2)
    freq_triples = dfg_alg.apply(log, parameters=parameters, variant=dfg_alg.Variants.FREQ_TRIPLES)
    performance_dfg = None
    if heu_net_decoration == "performance":
        performance_dfg = dfg_alg.apply(log, variant=dfg_alg.Variants.PERFORMANCE, parameters=parameters)

    return apply_heu_dfg(dfg, activities=activities, activities_occurrences=activities_occurrences,
                         start_activities=start_activities,
                         end_activities=end_activities, dfg_window_2=dfg_window_2, freq_triples=freq_triples,
                         performance_dfg=performance_dfg, parameters=parameters)


def apply_heu_pandas(df: pd.DataFrame, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> HeuristicsNet:
    """
    Discovers an Heuristics Net using Heuristics Miner

    Parameters
    ------------
    df
        Pandas dataframe
    parameters
        Possible parameters of the algorithm,
        including:
            - Parameters.ACTIVITY_KEY
            - Parameters.TIMESTAMP_KEY
            - Parameters.CASE_ID_KEY
            - Parameters.DEPENDENCY_THRESH
            - Parameters.AND_MEASURE_THRESH
            - Parameters.MIN_ACT_COUNT
            - Parameters.MIN_DFG_OCCURRENCES
            - Parameters.DFG_PRE_CLEANING_NOISE_THRESH
            - Parameters.LOOP_LENGTH_TWO_THRESH

    Returns
    ------------
    heu
        Heuristics Net
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes.DEFAULT_NAME_KEY)
    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters,
                                                     None)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes.DEFAULT_TIMESTAMP_KEY)

    from pm4py.algo.discovery.dfg.adapters.pandas import df_statistics, freq_triples as get_freq_triples
    from pm4py.statistics.attributes.pandas import get as pd_attributes
    from pm4py.statistics.start_activities.pandas import get as pd_sa_filter
    from pm4py.statistics.end_activities.pandas import get as pd_ea_filter

    start_activities = pd_sa_filter.get_start_activities(df, parameters=parameters)
    end_activities = pd_ea_filter.get_end_activities(df, parameters=parameters)
    activities_occurrences = pd_attributes.get_attribute_values(df, activity_key, parameters=parameters)
    activities = list(activities_occurrences.keys())
    heu_net_decoration = exec_utils.get_param_value(Parameters.HEU_NET_DECORATION, parameters, "frequency")

    if timestamp_key in df:
        dfg = df_statistics.get_dfg_graph(df, case_id_glue=case_id_glue,
                                          activity_key=activity_key, timestamp_key=timestamp_key,
                                          start_timestamp_key=start_timestamp_key)
        dfg_window_2 = df_statistics.get_dfg_graph(df, case_id_glue=case_id_glue,
                                                   activity_key=activity_key, timestamp_key=timestamp_key, window=2,
                                                   start_timestamp_key=start_timestamp_key)
        frequency_triples = get_freq_triples.get_freq_triples(df, case_id_glue=case_id_glue,
                                                              activity_key=activity_key,
                                                              timestamp_key=timestamp_key)

    else:
        dfg = df_statistics.get_dfg_graph(df, case_id_glue=case_id_glue,
                                          activity_key=activity_key, sort_timestamp_along_case_id=False)
        dfg_window_2 = df_statistics.get_dfg_graph(df, case_id_glue=case_id_glue,
                                                   activity_key=activity_key, sort_timestamp_along_case_id=False,
                                                   window=2)
        frequency_triples = get_freq_triples.get_freq_triples(df, case_id_glue=case_id_glue,
                                                              activity_key=activity_key,
                                                              timestamp_key=timestamp_key,
                                                              sort_timestamp_along_case_id=False)

    performance_dfg = None
    if heu_net_decoration == "performance":
        performance_dfg = df_statistics.get_dfg_graph(df, case_id_glue=case_id_glue,
                                                      activity_key=activity_key, timestamp_key=timestamp_key,
                                                      start_timestamp_key=start_timestamp_key,
                                                      measure="performance")

    heu_net = apply_heu_dfg(dfg, activities=activities, activities_occurrences=activities_occurrences,
                            start_activities=start_activities, end_activities=end_activities,
                            dfg_window_2=dfg_window_2,
                            freq_triples=frequency_triples, performance_dfg=performance_dfg, parameters=parameters)

    return heu_net


def apply_heu_dfg(dfg, activities=None, activities_occurrences=None, start_activities=None, end_activities=None,
                  dfg_window_2=None, freq_triples=None, performance_dfg=None, parameters=None) -> HeuristicsNet:
    """
    Discovers an Heuristics Net using Heuristics Miner

    Parameters
    ------------
    dfg
        Directly-Follows Graph
    activities
        (If provided) list of activities of the log
    activities_occurrences
        (If provided) dictionary of activities occurrences
    start_activities
        (If provided) dictionary of start activities occurrences
    end_activities
        (If provided) dictionary of end activities occurrences
    dfg_window_2
        (If provided) DFG of window 2
    freq_triples
        (If provided) Frequency triples
    performance_dfg
        (If provided) Performance DFG
    parameters
        Possible parameters of the algorithm,
        including:
            - Parameters.ACTIVITY_KEY
            - Parameters.TIMESTAMP_KEY
            - Parameters.CASE_ID_KEY
            - Parameters.DEPENDENCY_THRESH
            - Parameters.AND_MEASURE_THRESH
            - Parameters.MIN_ACT_COUNT
            - Parameters.MIN_DFG_OCCURRENCES
            - Parameters.DFG_PRE_CLEANING_NOISE_THRESH
            - Parameters.LOOP_LENGTH_TWO_THRESH

    Returns
    ------------
    heu
        Heuristics Net
    """
    if parameters is None:
        parameters = {}

    dependency_thresh = exec_utils.get_param_value(Parameters.DEPENDENCY_THRESH, parameters,
                                                   defaults.DEFAULT_DEPENDENCY_THRESH)
    and_measure_thresh = exec_utils.get_param_value(Parameters.AND_MEASURE_THRESH, parameters,
                                                    defaults.DEFAULT_AND_MEASURE_THRESH)
    min_act_count = exec_utils.get_param_value(Parameters.MIN_ACT_COUNT, parameters, defaults.DEFAULT_MIN_ACT_COUNT)
    min_dfg_occurrences = exec_utils.get_param_value(Parameters.MIN_DFG_OCCURRENCES, parameters,
                                                     defaults.DEFAULT_MIN_DFG_OCCURRENCES)
    dfg_pre_cleaning_noise_thresh = exec_utils.get_param_value(Parameters.DFG_PRE_CLEANING_NOISE_THRESH, parameters,
                                                               defaults.DEFAULT_DFG_PRE_CLEANING_NOISE_THRESH)
    loops_length_two_thresh = exec_utils.get_param_value(Parameters.LOOP_LENGTH_TWO_THRESH, parameters,
                                                         defaults.DEFAULT_LOOP_LENGTH_TWO_THRESH)
    heu_net = HeuristicsNet(dfg, activities=activities, activities_occurrences=activities_occurrences,
                            start_activities=start_activities, end_activities=end_activities,
                            dfg_window_2=dfg_window_2,
                            freq_triples=freq_triples, performance_dfg=performance_dfg)
    heu_net = calculate(heu_net, dependency_thresh=dependency_thresh, and_measure_thresh=and_measure_thresh,
                        min_act_count=min_act_count, min_dfg_occurrences=min_dfg_occurrences,
                        dfg_pre_cleaning_noise_thresh=dfg_pre_cleaning_noise_thresh,
                        loops_length_two_thresh=loops_length_two_thresh)

    return heu_net


def calculate(heu_net, dependency_thresh=defaults.DEFAULT_DEPENDENCY_THRESH,
              and_measure_thresh=defaults.DEFAULT_AND_MEASURE_THRESH, min_act_count=defaults.DEFAULT_MIN_ACT_COUNT,
              min_dfg_occurrences=defaults.DEFAULT_MIN_DFG_OCCURRENCES,
              dfg_pre_cleaning_noise_thresh=defaults.DEFAULT_DFG_PRE_CLEANING_NOISE_THRESH,
              loops_length_two_thresh=defaults.DEFAULT_LOOP_LENGTH_TWO_THRESH, parameters=None):
    """
    Calculate the dependency matrix, populate the nodes

    Parameters
    -------------
    dependency_thresh
        (Optional) dependency threshold
    and_measure_thresh
        (Optional) AND measure threshold
    min_act_count
        (Optional) minimum number of occurrences of an activity
    min_dfg_occurrences
        (Optional) minimum dfg occurrences
    dfg_pre_cleaning_noise_thresh
        (Optional) DFG pre cleaning noise threshold
    loops_length_two_thresh
        (Optional) loops length two threshold
    parameters
        Other parameters of the algorithm
    """
    if parameters is None:
        parameters = {}
    heu_net.min_dfg_occurrences = min_dfg_occurrences
    heu_net.dependency_matrix = None
    heu_net.dependency_matrix = {}
    heu_net.dfg_matrix = None
    heu_net.dfg_matrix = {}
    heu_net.performance_matrix = None
    heu_net.performance_matrix = {}
    if dfg_pre_cleaning_noise_thresh > 0.0:
        heu_net.dfg = clean_dfg_based_on_noise_thresh(heu_net.dfg, heu_net.activities, dfg_pre_cleaning_noise_thresh,
                                                      parameters=parameters)
    if heu_net.dfg_window_2 is not None:
        for el in heu_net.dfg_window_2:
            act1 = el[0]
            act2 = el[1]
            value = heu_net.dfg_window_2[el]
            if act1 not in heu_net.dfg_window_2_matrix:
                heu_net.dfg_window_2_matrix[act1] = {}
            heu_net.dfg_window_2_matrix[act1][act2] = value
    if heu_net.freq_triples is not None:
        for el in heu_net.freq_triples:
            act1 = el[0]
            act2 = el[1]
            act3 = el[2]
            value = heu_net.freq_triples[el]
            # avoid to consider self-loops
            if act1 == act3 and not act1 == act2:
                if act1 not in heu_net.freq_triples_matrix:
                    heu_net.freq_triples_matrix[act1] = {}
                heu_net.freq_triples_matrix[act1][act2] = value
    for el in heu_net.dfg:
        act1 = el[0]
        act2 = el[1]
        value = heu_net.dfg[el]
        perf_value = heu_net.performance_dfg[el] if heu_net.performance_dfg is not None else heu_net.dfg[el]
        if act1 not in heu_net.dependency_matrix:
            heu_net.dependency_matrix[act1] = {}
            heu_net.dfg_matrix[act1] = {}
            heu_net.performance_matrix[act1] = {}
        heu_net.dfg_matrix[act1][act2] = value
        heu_net.performance_matrix[act1][act2] = perf_value
        if not act1 == act2:
            inv_couple = (act2, act1)
            c1 = value
            if inv_couple in heu_net.dfg:
                c2 = heu_net.dfg[inv_couple]
                dep = (c1 - c2) / (c1 + c2 + 1)
            else:
                dep = c1 / (c1 + 1)
        else:
            dep = value / (value + 1)
        heu_net.dependency_matrix[act1][act2] = dep
    for n1 in heu_net.dependency_matrix:
        for n2 in heu_net.dependency_matrix[n1]:
            condition1 = n1 in heu_net.activities_occurrences and heu_net.activities_occurrences[n1] >= min_act_count
            condition2 = n2 in heu_net.activities_occurrences and heu_net.activities_occurrences[n2] >= min_act_count
            condition3 = heu_net.dfg_matrix[n1][n2] >= min_dfg_occurrences
            condition4 = heu_net.dependency_matrix[n1][n2] >= dependency_thresh
            condition = condition1 and condition2 and condition3 and condition4
            if condition:
                if n1 not in heu_net.nodes:
                    heu_net.nodes[n1] = Node(heu_net, n1, heu_net.activities_occurrences[n1],
                                             is_start_node=(n1 in heu_net.start_activities),
                                             is_end_node=(n1 in heu_net.end_activities),
                                             default_edges_color=heu_net.default_edges_color[0],
                                             node_type=heu_net.node_type, net_name=heu_net.net_name[0],
                                             nodes_dictionary=heu_net.nodes)
                if n2 not in heu_net.nodes:
                    heu_net.nodes[n2] = Node(heu_net, n2, heu_net.activities_occurrences[n2],
                                             is_start_node=(n2 in heu_net.start_activities),
                                             is_end_node=(n2 in heu_net.end_activities),
                                             default_edges_color=heu_net.default_edges_color[0],
                                             node_type=heu_net.node_type, net_name=heu_net.net_name[0],
                                             nodes_dictionary=heu_net.nodes)

                repr_value = heu_net.performance_matrix[n1][n2]
                heu_net.nodes[n1].add_output_connection(heu_net.nodes[n2], heu_net.dependency_matrix[n1][n2],
                                                        heu_net.dfg_matrix[n1][n2], repr_value=repr_value)
                heu_net.nodes[n2].add_input_connection(heu_net.nodes[n1], heu_net.dependency_matrix[n1][n2],
                                                       heu_net.dfg_matrix[n1][n2], repr_value=repr_value)
    for node in heu_net.nodes:
        heu_net.nodes[node].calculate_and_measure_out(and_measure_thresh=and_measure_thresh)
        heu_net.nodes[node].calculate_and_measure_in(and_measure_thresh=and_measure_thresh)
        heu_net.nodes[node].calculate_loops_length_two(heu_net.dfg_matrix, heu_net.freq_triples_matrix,
                                                       loops_length_two_thresh=loops_length_two_thresh)
    nodes = list(heu_net.nodes.keys())
    added_loops = set()
    for n1 in nodes:
        for n2 in heu_net.nodes[n1].loop_length_two:
            if n1 in heu_net.dfg_matrix and n2 in heu_net.dfg_matrix[n1] and heu_net.dfg_matrix[n1][
                n2] >= min_dfg_occurrences and n1 in heu_net.activities_occurrences and heu_net.activities_occurrences[
                n1] >= min_act_count and n2 in heu_net.activities_occurrences and heu_net.activities_occurrences[
                n2] >= min_act_count:
                if not ((n1 in heu_net.dependency_matrix and n2 in heu_net.dependency_matrix[n1] and
                         heu_net.dependency_matrix[n1][n2] >= dependency_thresh) or (
                                n2 in heu_net.dependency_matrix and n1 in heu_net.dependency_matrix[n2] and
                                heu_net.dependency_matrix[n2][n1] >= dependency_thresh)):
                    if n2 not in heu_net.nodes:
                        heu_net.nodes[n2] = Node(heu_net, n2, heu_net.activities_occurrences[n2],
                                                 is_start_node=(n2 in heu_net.start_activities),
                                                 is_end_node=(n2 in heu_net.end_activities),
                                                 default_edges_color=heu_net.default_edges_color[0],
                                                 node_type=heu_net.node_type, net_name=heu_net.net_name[0],
                                                 nodes_dictionary=heu_net.nodes)
                    v_n1_n2 = heu_net.dfg_matrix[n1][n2] if n1 in heu_net.dfg_matrix and n2 in heu_net.dfg_matrix[
                        n1] else 0
                    v_n2_n1 = heu_net.dfg_matrix[n2][n1] if n2 in heu_net.dfg_matrix and n1 in heu_net.dfg_matrix[
                        n2] else 0

                    if (n1, n2) not in added_loops:
                        repr_value = heu_net.performance_matrix[n1][n2] if n1 in heu_net.performance_matrix and n2 in \
                                                                           heu_net.performance_matrix[n1] else 0
                        added_loops.add((n1, n2))
                        heu_net.nodes[n1].add_output_connection(heu_net.nodes[n2], 0,
                                                                v_n1_n2, repr_value=repr_value)
                        heu_net.nodes[n2].add_input_connection(heu_net.nodes[n1], 0,
                                                               v_n2_n1, repr_value=repr_value)

                    if (n2, n1) not in added_loops:
                        repr_value = heu_net.performance_matrix[n2][n1] if n2 in heu_net.performance_matrix and n1 in \
                                                                           heu_net.performance_matrix[n2] else 0
                        added_loops.add((n2, n1))
                        heu_net.nodes[n2].add_output_connection(heu_net.nodes[n1], 0,
                                                                v_n2_n1, repr_value=repr_value)
                        heu_net.nodes[n1].add_input_connection(heu_net.nodes[n2], 0,
                                                               v_n1_n2, repr_value=repr_value)
    if len(heu_net.nodes) == 0:
        for act in heu_net.activities:
            heu_net.nodes[act] = Node(heu_net, act, heu_net.activities_occurrences[act],
                                      is_start_node=(act in heu_net.start_activities),
                                      is_end_node=(act in heu_net.end_activities),
                                      default_edges_color=heu_net.default_edges_color[0],
                                      node_type=heu_net.node_type, net_name=heu_net.net_name[0],
                                      nodes_dictionary=heu_net.nodes)

    return heu_net

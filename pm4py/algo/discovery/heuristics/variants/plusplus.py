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
from copy import copy
from enum import Enum
from typing import Optional, Dict, Any, Tuple

import pandas as pd

from pm4py.algo.discovery.dfg import algorithm as dfg_alg
from pm4py.algo.discovery.dfg.adapters.pandas import df_statistics
from pm4py.objects.conversion.heuristics_net import converter as hn_conv_alg
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.heuristics_net import defaults
from pm4py.objects.heuristics_net.obj import HeuristicsNet
from pm4py.objects.heuristics_net.node import Node
from pm4py.objects.log.obj import EventLog
from pm4py.objects.log.util import interval_lifecycle
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.statistics.attributes.log import get as log_attributes
from pm4py.statistics.attributes.pandas import get as pd_attributes
from pm4py.statistics.concurrent_activities.log import get as conc_act_get
from pm4py.statistics.concurrent_activities.pandas import get as pd_conc_act
from pm4py.statistics.end_activities.log import get as log_ea
from pm4py.statistics.end_activities.pandas import get as pd_ea
from pm4py.statistics.eventually_follows.log import get as efg_get
from pm4py.statistics.eventually_follows.pandas import get as pd_efg
from pm4py.statistics.service_time.log import get as soj_get
from pm4py.statistics.service_time.pandas import get as pd_soj_time
from pm4py.statistics.start_activities.log import get as log_sa
from pm4py.statistics.start_activities.pandas import get as pd_sa
from pm4py.util import exec_utils, constants, xes_constants as xes


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    DEPENDENCY_THRESH = "dependency_thresh"
    AND_MEASURE_THRESH = "and_measure_thresh"
    MIN_ACT_COUNT = "min_act_count"
    MIN_DFG_OCCURRENCES = "min_dfg_occurrences"
    HEU_NET_DECORATION = "heu_net_decoration"


def apply(log: EventLog, parameters: Optional[Dict[Any, Any]] = None) -> Tuple[PetriNet, Marking, Marking]:
    """
    Discovers a Petri net using the Heuristics Miner ++ algorithm

    Implements the approach described in
    Burattin, Andrea, and Alessandro Sperduti. "Heuristics Miner for Time Intervals." ESANN. 2010.

    https://andrea.burattin.net/public-files/publications/2010-esann-slides.pdf

    Parameters
    --------------
    log
        Event log
    parameters
        Parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY
        - Parameters.START_TIMESTAMP_KEY
        - Parameters.TIMESTAMP_KEY
        - Parameters.DEPENDENCY_THRESH
        - Parameters.AND_MEASURE_THRESH
        - Parameters.MIN_ACT_COUNT
        - Parameters.MIN_DFG_OCCURRENCES
        - Parameters.HEU_NET_DECORATION

    Returns
    --------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    """
    heu_net = apply_heu(log, parameters=parameters)
    net, im, fm = hn_conv_alg.apply(heu_net, parameters=parameters)
    return net, im, fm


def apply_pandas(df: pd.DataFrame, parameters: Optional[Dict[Any, Any]] = None) -> Tuple[PetriNet, Marking, Marking]:
    """
    Discovers a Petri net using the Heuristics Miner ++ algorithm

    Implements the approach described in
    Burattin, Andrea, and Alessandro Sperduti. "Heuristics Miner for Time Intervals." ESANN. 2010.

    https://andrea.burattin.net/public-files/publications/2010-esann-slides.pdf

    Parameters
    --------------
    df
        Dataframe
    parameters
        Parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY
        - Parameters.START_TIMESTAMP_KEY
        - Parameters.TIMESTAMP_KEY
        - Parameters.CASE_ID_KEY
        - Parameters.DEPENDENCY_THRESH
        - Parameters.AND_MEASURE_THRESH
        - Parameters.MIN_ACT_COUNT
        - Parameters.MIN_DFG_OCCURRENCES
        - Parameters.HEU_NET_DECORATION

    Returns
    --------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    """
    heu_net = apply_heu_pandas(df, parameters=parameters)
    net, im, fm = hn_conv_alg.apply(heu_net, parameters=parameters)
    return net, im, fm


def apply_heu(log: EventLog, parameters: Optional[Dict[Any, Any]] = None) -> HeuristicsNet:
    """
    Discovers an heuristics net using the Heuristics Miner ++ algorithm

    Implements the approach described in
    Burattin, Andrea, and Alessandro Sperduti. "Heuristics Miner for Time Intervals." ESANN. 2010.

    https://andrea.burattin.net/public-files/publications/2010-esann-slides.pdf

    Parameters
    --------------
    log
        Event log
    parameters
        Parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY
        - Parameters.START_TIMESTAMP_KEY
        - Parameters.TIMESTAMP_KEY
        - Parameters.DEPENDENCY_THRESH
        - Parameters.AND_MEASURE_THRESH
        - Parameters.MIN_ACT_COUNT
        - Parameters.MIN_DFG_OCCURRENCES
        - Parameters.HEU_NET_DECORATION

    Returns
    --------------
    heu_net
        Heuristics net
    """
    if parameters is None:
        parameters = {}

    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)
    log = interval_lifecycle.to_interval(log, parameters=parameters)
    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters,
                                                     None)
    if start_timestamp_key is None:
        start_timestamp_key = xes.DEFAULT_START_TIMESTAMP_KEY
        parameters = copy(parameters)
        parameters[Parameters.START_TIMESTAMP_KEY] = start_timestamp_key
    start_activities, end_activities, activities_occurrences, dfg, performance_dfg, sojourn_time, concurrent_activities = discover_abstraction_log(
        log, parameters=parameters)
    return discover_heu_net_plus_plus(start_activities, end_activities, activities_occurrences, dfg, performance_dfg,
                                      sojourn_time, concurrent_activities, parameters=parameters)


def discover_abstraction_log(log: EventLog, parameters: Optional[Dict[Any, Any]] = None) -> Tuple[
    Any, Any, Any, Any, Any, Any, Any]:
    """
    Discovers an abstraction from a log that is useful for the Heuristics Miner ++ algorithm

    Parameters
    --------------
    log
        Event log
    parameters
        Parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY
        - Parameters.START_TIMESTAMP_KEY
        - Parameters.TIMESTAMP_KEY
        - Parameters.CASE_ID_KEY

    Returns
    --------------
    start_activities
        Start activities
    end_activities
        End activities
    activities_occurrences
        Activities along with their number of occurrences
    dfg
        Directly-follows graph
    performance_dfg
        (Performance) Directly-follows graph
    sojourn_time
        Sojourn time for each activity
    concurrent_activities
        Concurrent activities
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes.DEFAULT_NAME_KEY)
    start_activities = log_sa.get_start_activities(log, parameters=parameters)
    end_activities = log_ea.get_end_activities(log, parameters=parameters)
    activities_occurrences = log_attributes.get_attribute_values(log, activity_key, parameters=parameters)
    efg_parameters = copy(parameters)
    efg_parameters[efg_get.Parameters.KEEP_FIRST_FOLLOWING] = True
    dfg = efg_get.apply(log, parameters=efg_parameters)
    performance_dfg = dfg_alg.apply(log, variant=dfg_alg.Variants.PERFORMANCE, parameters=parameters)
    sojourn_time = soj_get.apply(log, parameters=parameters)
    concurrent_activities = conc_act_get.apply(log, parameters=parameters)
    return (
        start_activities, end_activities, activities_occurrences, dfg, performance_dfg, sojourn_time,
        concurrent_activities)


def apply_heu_pandas(df: pd.DataFrame, parameters: Optional[Dict[Any, Any]] = None) -> HeuristicsNet:
    """
    Discovers an heuristics net using the Heuristics Miner ++ algorithm

    Implements the approach described in
    Burattin, Andrea, and Alessandro Sperduti. "Heuristics Miner for Time Intervals." ESANN. 2010.

    https://andrea.burattin.net/public-files/publications/2010-esann-slides.pdf

    Parameters
    --------------
    df
        Dataframe
    parameters
        Parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY
        - Parameters.START_TIMESTAMP_KEY
        - Parameters.TIMESTAMP_KEY
        - Parameters.CASE_ID_KEY
        - Parameters.DEPENDENCY_THRESH
        - Parameters.AND_MEASURE_THRESH
        - Parameters.MIN_ACT_COUNT
        - Parameters.MIN_DFG_OCCURRENCES
        - Parameters.HEU_NET_DECORATION

    Returns
    --------------
    heu_net
        Heuristics net
    """
    if parameters is None:
        parameters = {}
    start_activities, end_activities, activities_occurrences, dfg, performance_dfg, sojourn_time, concurrent_activities = discover_abstraction_dataframe(
        df, parameters=parameters)
    return discover_heu_net_plus_plus(start_activities, end_activities, activities_occurrences, dfg, performance_dfg,
                                      sojourn_time, concurrent_activities, parameters=parameters)


def discover_abstraction_dataframe(df: pd.DataFrame, parameters: Optional[Dict[Any, Any]] = None) -> Tuple[
    Any, Any, Any, Any, Any, Any, Any]:
    """
    Discovers an abstraction from a dataframe that is useful for the Heuristics Miner ++ algorithm

    Parameters
    --------------
    df
        Dataframe
    parameters
        Parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY
        - Parameters.START_TIMESTAMP_KEY
        - Parameters.TIMESTAMP_KEY
        - Parameters.CASE_ID_KEY

    Returns
    --------------
    start_activities
        Start activities
    end_activities
        End activities
    activities_occurrences
        Activities along with their number of occurrences
    dfg
        Directly-follows graph
    performance_dfg
        (Performance) Directly-follows graph
    sojourn_time
        Sojourn time for each activity
    concurrent_activities
        Concurrent activities
    """
    if parameters is None:
        parameters = {}
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes.DEFAULT_NAME_KEY)
    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters,
                                                     None)
    if start_timestamp_key is None:
        start_timestamp_key = xes.DEFAULT_START_TIMESTAMP_KEY
        parameters = copy(parameters)
        parameters[Parameters.START_TIMESTAMP_KEY] = start_timestamp_key
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes.DEFAULT_TIMESTAMP_KEY)
    case_id_glue = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
    start_activities = pd_sa.get_start_activities(df, parameters=parameters)
    end_activities = pd_ea.get_end_activities(df, parameters=parameters)
    activities_occurrences = pd_attributes.get_attribute_values(df, activity_key, parameters=parameters)
    efg_parameters = copy(parameters)
    efg_parameters[pd_efg.Parameters.KEEP_FIRST_FOLLOWING] = True
    dfg = pd_efg.apply(df, parameters=efg_parameters)
    performance_dfg = df_statistics.get_dfg_graph(df, case_id_glue=case_id_glue,
                                                  activity_key=activity_key, timestamp_key=timestamp_key,
                                                  start_timestamp_key=start_timestamp_key, measure="performance")
    sojourn_time = pd_soj_time.apply(df, parameters=parameters)
    concurrent_activities = pd_conc_act.apply(df, parameters=parameters)
    return (
        start_activities, end_activities, activities_occurrences, dfg, performance_dfg, sojourn_time,
        concurrent_activities)


def discover_heu_net_plus_plus(start_activities, end_activities, activities_occurrences, dfg, performance_dfg,
                               sojourn_time, concurrent_activities, parameters: Optional[Dict[Any, Any]] = None):
    """
    Discovers an heuristics net using the Heuristics Miner ++ algorithm

    Implements the approach described in
    Burattin, Andrea, and Alessandro Sperduti. "Heuristics Miner for Time Intervals." ESANN. 2010.

    https://andrea.burattin.net/public-files/publications/2010-esann-slides.pdf

    Parameters
    --------------
    start_activities
        Start activities
    end_activities
        End activities
    activities_occurrences
        Activities along with their number of occurrences
    dfg
        Directly-follows graph
    performance_dfg
        (Performance) Directly-follows graph
    sojourn_time
        Sojourn time for each activity
    concurrent_activities
        Concurrent activities
    parameters
        Parameters of the algorithm, including:
        - Parameters.DEPENDENCY_THRESH
        - Parameters.AND_MEASURE_THRESH
        - Parameters.MIN_ACT_COUNT
        - Parameters.MIN_DFG_OCCURRENCES
        - Parameters.HEU_NET_DECORATION

    Returns
    --------------
    heu_net
        Heuristics net
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
    heu_net_decoration = exec_utils.get_param_value(Parameters.HEU_NET_DECORATION, parameters, "frequency")

    # filter on activity and paths occurrence
    activities_occurrences = {x: y for x, y in activities_occurrences.items() if y >= min_act_count}
    dfg = {x: y for x, y in dfg.items() if
           y >= min_dfg_occurrences and x[0] in activities_occurrences and x[1] in activities_occurrences}
    performance_dfg = {x: y for x, y in performance_dfg.items() if x in dfg}
    start_activities = {x: y for x, y in start_activities.items() if x in activities_occurrences}
    end_activities = {x: y for x, y in end_activities.items() if x in activities_occurrences}
    activities = list(activities_occurrences.keys())
    if heu_net_decoration == "frequency":
        heu_net = HeuristicsNet(dfg, activities=activities, activities_occurrences=activities_occurrences,
                                start_activities=start_activities, end_activities=end_activities)
    else:
        heu_net = HeuristicsNet(dfg, activities=activities, activities_occurrences=activities_occurrences,
                                start_activities=start_activities, end_activities=end_activities,
                                performance_dfg=performance_dfg)
    heu_net.min_dfg_occurrences = min_dfg_occurrences
    heu_net.sojourn_times = sojourn_time
    heu_net.concurrent_activities = concurrent_activities
    return calculate(heu_net, dependency_thresh, and_measure_thresh, heu_net_decoration)


def calculate(heu_net: HeuristicsNet, dependency_thresh: float, and_measure_thresh: float,
              heu_net_decoration: str) -> HeuristicsNet:
    """
    Calculates the dependency matrix and the AND measures using the Heuristics Miner ++ formulas

    Parameters
    ----------------
    heu_net
        Heuristics net
    dependency_thresh
        Dependency threshold
    and_measure_thresh
        AND measure threshold
    heu_net_decoration
        Decoration to use (frequency/performance)

    Returns
    ----------------
    heu_net
        Heuristics net
    """
    heu_net.performance_matrix = {}
    heu_net.dependency_matrix = {}
    heu_net.dfg_matrix = {}
    for el in heu_net.dfg:
        act1 = el[0]
        act2 = el[1]
        if act1 not in heu_net.dfg_matrix:
            heu_net.dfg_matrix[act1] = {}
            heu_net.dependency_matrix[act1] = {}
            heu_net.performance_matrix[act1] = {}
        heu_net.dfg_matrix[act1][act2] = heu_net.dfg[el]
        heu_net.dependency_matrix[act1][act2] = -1
        heu_net.performance_matrix[act1][act2] = heu_net.performance_dfg[el] if heu_net.performance_dfg and el in heu_net.performance_dfg else 0.0
    for act1 in heu_net.activities:
        heu_net.nodes[act1] = Node(heu_net, act1, heu_net.activities_occurrences[act1], node_type=heu_net.node_type)
    # calculates the dependencies between the activities
    heu_net = calculate_dependency(heu_net, dependency_thresh, heu_net_decoration)
    # calculates the AND measure for outgoing edges (e.g. which activities happen in parallel after a given activity)
    heu_net = calculate_and_out_measure(heu_net, and_measure_thresh)
    # calculates the AND measure for ingoing edges (e.g. which activities happen in parallel before a given activity)
    heu_net = calculate_and_in_measure(heu_net, and_measure_thresh)
    return heu_net


def calculate_dependency(heu_net: HeuristicsNet, dependency_thresh: float, heu_net_decoration: str) -> HeuristicsNet:
    """
    Calculates the dependency matrix using the Heuristics Miner ++ formula

    Parameters
    --------------
    heu_net
        Heuristics net
    dependency_thresh
        Dependency threshold
    heu_net_decoration
        Decoration to include (frequency/performance)

    Returns
    ---------------
    heu_net
        Heuristics net (enriched)
    """
    for act1 in heu_net.activities:
        if act1 in heu_net.dfg_matrix:
            for act2 in heu_net.dfg_matrix[act1]:
                v1 = heu_net.dfg_matrix[act1][act2]
                v2 = heu_net.dfg_matrix[act2][act1] if act2 in heu_net.dfg_matrix and act1 in heu_net.dfg_matrix[
                    act2] else 0.0
                tup = tuple(sorted((act1, act2)))
                # added term for Heuristics Miner ++
                v3 = heu_net.concurrent_activities[tup] if tup in heu_net.concurrent_activities else 0.0
                dep = (v1 - v2) / (v1 + v2 + v3)
                heu_net.dependency_matrix[act1][act2] = dep
                if dep > dependency_thresh:
                    repr_value = v1 if heu_net_decoration == "frequency" else heu_net.performance_matrix[act1][act2]
                    heu_net.nodes[act1].add_output_connection(heu_net.nodes[act2], dep, v1, repr_value=repr_value)
                    heu_net.nodes[act2].add_input_connection(heu_net.nodes[act1], dep, v1, repr_value=repr_value)
    return heu_net


def calculate_and_out_measure(heu_net: HeuristicsNet, and_measure_thresh: float) -> HeuristicsNet:
    """
    Calculates the AND measure for outgoing edges using the Heuristics Miner ++ formula

    Parameters
    ---------------
    heu_net
        Heuristics net
    and_measure_thresh
        And measure threshold

    Returns
    ---------------
    heu_net
        Heuristics net (enriched)
    """
    for act in heu_net.nodes:
        nodes = sorted(x.node_name for x in heu_net.nodes[act].output_connections)
        i = 0
        while i < len(nodes):
            n1 = nodes[i]
            v3 = heu_net.dfg_matrix[act][n1] if act in heu_net.dfg_matrix and n1 in heu_net.dfg_matrix[act] else 0.0
            j = i + 1
            while j < len(nodes):
                n2 = nodes[j]
                tup = tuple(sorted((n1, n2)))
                v1 = heu_net.dfg_matrix[n1][n2] if n1 in heu_net.dfg_matrix and n2 in heu_net.dfg_matrix[n1] else 0.0
                v2 = heu_net.dfg_matrix[n2][n1] if n2 in heu_net.dfg_matrix and n1 in heu_net.dfg_matrix[n2] else 0.0
                v4 = heu_net.dfg_matrix[act][n2] if act in heu_net.dfg_matrix and n2 in heu_net.dfg_matrix[act] else 0.0
                # added term for Heuristics Miner ++
                v5 = heu_net.concurrent_activities[tup] if tup in heu_net.concurrent_activities else 0.0
                this_value = (v1 + v2 + v5) / (v3 + v4)
                if this_value > and_measure_thresh:
                    if n1 not in heu_net.nodes[act].and_measures_out:
                        heu_net.nodes[act].and_measures_out[n1] = {}
                    heu_net.nodes[act].and_measures_out[n1][n2] = this_value
                j = j + 1
            i = i + 1
    return heu_net


def calculate_and_in_measure(heu_net: HeuristicsNet, and_measure_thresh: float) -> HeuristicsNet:
    """
    Calculates the AND measure for incoming edges using the Heuristics Miner ++ formula

    Parameters
    ---------------
    heu_net
        Heuristics net
    and_measure_thresh
        And measure threshold

    Returns
    ---------------
    heu_net
        Heuristics net (enriched)
    """
    for act in heu_net.nodes:
        nodes = sorted(x.node_name for x in heu_net.nodes[act].input_connections)
        i = 0
        while i < len(nodes):
            n1 = nodes[i]
            v3 = heu_net.dfg_matrix[n1][act] if n1 in heu_net.dfg_matrix and act in heu_net.dfg_matrix[n1] else 0.0
            j = i + 1
            while j < len(nodes):
                n2 = nodes[j]
                tup = tuple(sorted((n1, n2)))
                v1 = heu_net.dfg_matrix[n1][n2] if n1 in heu_net.dfg_matrix and n2 in heu_net.dfg_matrix[n1] else 0.0
                v2 = heu_net.dfg_matrix[n2][n1] if n2 in heu_net.dfg_matrix and n1 in heu_net.dfg_matrix[n2] else 0.0
                v4 = heu_net.dfg_matrix[n2][act] if n2 in heu_net.dfg_matrix and act in heu_net.dfg_matrix[n2] else 0.0
                # added term for Heuristics Miner ++
                v5 = heu_net.concurrent_activities[tup] if tup in heu_net.concurrent_activities else 0.0
                this_value = (v1 + v2 + v5) / (v3 + v4)
                if this_value > and_measure_thresh:
                    if n1 not in heu_net.nodes[act].and_measures_in:
                        heu_net.nodes[act].and_measures_in[n1] = {}
                    heu_net.nodes[act].and_measures_in[n1][n2] = this_value
                j = j + 1
            i = i + 1
    return heu_net


def apply_dfg(dfg, activities=None, activities_occurrences=None, start_activities=None, end_activities=None,
              parameters=None):
    raise Exception("not implemented for plusplus version")


def apply_heu_dfg(dfg, activities=None, activities_occurrences=None, start_activities=None, end_activities=None,
                  dfg_window_2=None, freq_triples=None, parameters=None):
    raise Exception("not implemented for plusplus version")

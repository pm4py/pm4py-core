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
import datetime
import heapq
import math
import sys
import time
from collections import Counter
from copy import deepcopy
from enum import Enum
from typing import Optional, Dict, Any, Union, Tuple

from pm4py.objects.log.obj import EventLog
from pm4py.objects.log.obj import Trace, Event
from pm4py.util import exec_utils, constants, xes_constants
from pm4py.util.dt_parsing.variants import strpfromiso


class Parameters(Enum):
    MAX_NO_VARIANTS = "max_no_variants"
    MIN_WEIGHTED_PROBABILITY = "min_weighted_probability"
    MAX_NO_OCC_PER_ACTIVITY = "max_no_occ_per_activitiy"
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    INTERRUPT_SIMULATION_WHEN_DFG_COMPLETE = "interrupt_simulation_when_dfg_complete"
    ADD_TRACE_IF_TAKES_NEW_ELS_TO_DFG = "add_trace_if_takes_new_els_to_dfg"
    RETURN_VARIANTS = "return_variants"
    MAX_EXECUTION_TIME = "max_execution_time"
    RETURN_ONLY_IF_COMPLETE = "return_only_if_complete"
    MIN_VARIANT_OCC = "min_variant_occ"


def get_node_tr_probabilities(dfg, start_activities, end_activities):
    """
    Gets the transition probabilities between the nodes of a DFG

    Parameters
    --------------
    dfg
        DFG
    start_activities
        Start activities
    end_activities
        End activities

    Returns
    ---------------
    weighted_start_activities
        Start activities, with a relative weight going from 0 to 1
    node_transition_probabilities
        The transition probabilities between the nodes of the DFG
        (the end node is None)
    """
    node_transition_probabilities = {}
    # this part gives to each edge a transition probability,
    # given the (integer) DFG and the (integer) count of the end activities
    for el in dfg:
        if el[0] not in node_transition_probabilities:
            node_transition_probabilities[el[0]] = {}
        node_transition_probabilities[el[0]][el[1]] = dfg[el]
    for ea in end_activities:
        if ea not in node_transition_probabilities:
            node_transition_probabilities[ea] = {}
        node_transition_probabilities[ea][None] = end_activities[ea]
    for source in node_transition_probabilities:
        sum_values = sum(node_transition_probabilities[source].values())
        for target in node_transition_probabilities[source]:
            # logarithm gives numerical stability
            node_transition_probabilities[source][target] = math.log(float(
                node_transition_probabilities[source][target]) / float(sum_values))
    # this part gives to each start activity a probability, given its frequency
    sum_start_act = sum(start_activities.values())
    start_activities = deepcopy(start_activities)
    for sa in start_activities:
        start_activities[sa] = math.log(float(start_activities[sa]) / float(sum_start_act))

    return start_activities, node_transition_probabilities


def get_traces(dfg, start_activities, end_activities, parameters=None):
    """
    Gets the most probable traces from the DFG, one-by-one (iterator),
    until the least probable

    Parameters
    ---------------
    dfg
        *Complete* DFG
    start_activities
        Start activities
    end_activities
        End activities
    parameters
        Parameters of the algorithm, including:
        - Parameters.MAX_NO_OCC_PER_ACTIVITY => the maximum number of occurrences per activity in the traces of the log
                                                (default: 2)

    Returns
    ---------------
    yielded_trace
        Trace of the simulation
    """
    if parameters is None:
        parameters = {}

    max_no_occ_per_activity = exec_utils.get_param_value(Parameters.MAX_NO_OCC_PER_ACTIVITY, parameters, 2)

    start_activities, node_transition_probabilities = get_node_tr_probabilities(dfg, start_activities, end_activities)

    # we start from the partial traces containing only the start activities along
    # with their probability
    partial_traces = [(-start_activities[sa], (sa,)) for sa in start_activities]
    heapq.heapify(partial_traces)

    while partial_traces:
        trace = heapq.heappop(partial_traces)
        trace = list(trace)
        trace[1] = list(trace[1])
        trace_counter = Counter(trace[1])
        last_act = trace[1][-1]
        prob = trace[0]

        for new_act in node_transition_probabilities[last_act]:
            if trace_counter[new_act] < max_no_occ_per_activity:
                prob_new_act = node_transition_probabilities[last_act][new_act]
                if new_act is None:
                    p = math.exp(-(prob - prob_new_act))
                    tr = tuple(trace[1])
                    yield (tr, p)
                else:
                    heapq.heappush(partial_traces, (prob - prob_new_act, tuple(trace[1] + [new_act])))


def apply(dfg: Dict[Tuple[str, str], int], start_activities: Dict[str, int], end_activities: Dict[str, int],
          parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Union[
    EventLog, Dict[Tuple[str, str], int]]:
    """
    Applies the playout algorithm on a DFG, extracting the most likely traces according to the DFG

    Parameters
    ---------------
    dfg
        *Complete* DFG
    start_activities
        Start activities
    end_activities
        End activities
    parameters
        Parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY => the activity key of the simulated log
        - Parameters.TIMESTAMP_KEY => the timestamp key of the simulated log
        - Parameters.MAX_NO_VARIANTS => the maximum number of variants generated by the method (default: 3000)
        - Parameters.MIN_WEIGHTED_PROBABILITY => the minimum overall weighted probability that makes the method stop
                                                (default: 1)
        - Parameters.MAX_NO_OCC_PER_ACTIVITY => the maximum number of occurrences per activity in the traces of the log
                                                (default: 2)
        - Parameters.INTERRUPT_SIMULATION_WHEN_DFG_COMPLETE => interrupts the simulation when the DFG of the simulated
                                                    log has the same keys to the DFG of the original log
                                                    (all behavior is contained) (default: False)
        - Parameters.ADD_TRACE_IF_TAKES_NEW_ELS_TO_DFG => adds a simulated trace to the simulated log only if it adds
                                                    elements to the simulated DFG, e.g., it adds behavior;
                                                    skip insertion otherwise (default: False)
        - Parameters.RETURN_VARIANTS => returns the traces as variants with a likely number of occurrences

    Returns
    ---------------
    simulated_log
        Simulated log
    """
    if parameters is None:
        parameters = {}

    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    max_no_variants = exec_utils.get_param_value(Parameters.MAX_NO_VARIANTS, parameters, 3000)
    min_weighted_probability = exec_utils.get_param_value(Parameters.MIN_WEIGHTED_PROBABILITY, parameters, 1.0)
    interrupt_simulation_when_dfg_complete = exec_utils.get_param_value(
        Parameters.INTERRUPT_SIMULATION_WHEN_DFG_COMPLETE, parameters, False)
    add_trace_if_takes_new_els_to_dfg = exec_utils.get_param_value(Parameters.ADD_TRACE_IF_TAKES_NEW_ELS_TO_DFG,
                                                                   parameters, False)
    return_variants = exec_utils.get_param_value(Parameters.RETURN_VARIANTS, parameters, False)
    max_execution_time = exec_utils.get_param_value(Parameters.MAX_EXECUTION_TIME, parameters, sys.maxsize)
    return_only_if_complete = exec_utils.get_param_value(Parameters.RETURN_ONLY_IF_COMPLETE, parameters, False)
    min_variant_occ = exec_utils.get_param_value(Parameters.MIN_VARIANT_OCC, parameters, 1)

    # keep track of the DFG, start activities and end activities of the (ongoing) simulation
    simulated_traces_dfg = set()
    simulated_traces_sa = set()
    simulated_traces_ea = set()
    interrupt_break_condition = False
    interrupted = False
    overall_probability = 0.0

    final_traces = []
    max_occ = 0

    start_time = time.time()
    for tr, p in get_traces(dfg, start_activities, end_activities, parameters=parameters):
        if interrupt_simulation_when_dfg_complete and interrupt_break_condition:
            break
        if len(final_traces) >= max_no_variants:
            interrupted = True
            break
        if overall_probability > min_weighted_probability:
            interrupted = True
            break
        current_time = time.time()
        if (current_time - start_time) > max_execution_time:
            interrupted = True
            break
        overall_probability += p
        diff_sa = {tr[0]}.difference(simulated_traces_sa)
        diff_ea = {tr[-1]}.difference(simulated_traces_ea)
        diff_dfg = {(tr[i], tr[i + 1]) for i in range(len(tr) - 1)}.difference(simulated_traces_dfg)
        adds_something = len(diff_sa) > 0 or len(diff_ea) > 0 or len(diff_dfg) > 0
        if add_trace_if_takes_new_els_to_dfg and not adds_something:
            # interrupt the addition if the ADD_TRACE_IF_TAKES_NEW_ELS_TO_DFG is set to True,
            # and the trace does not really change the information on the DFG, start activities,
            # end activities
            continue
        # update the start activities, end activities, DFG of the original log
        simulated_traces_sa = simulated_traces_sa.union(diff_sa)
        simulated_traces_ea = simulated_traces_ea.union(diff_ea)
        simulated_traces_dfg = simulated_traces_dfg.union(diff_dfg)
        # memorize the difference between the original DFG and the DFG of the simulated log
        diff_original_sa = set(start_activities).difference(simulated_traces_sa)
        diff_original_ea = set(end_activities).difference(simulated_traces_ea)
        diff_original_dfg = set(dfg).difference(simulated_traces_dfg)
        interrupt_break_condition = len(diff_original_sa) == 0 and len(diff_original_ea) == 0 and len(
            diff_original_dfg) == 0
        var_occ = math.ceil(p * max_no_variants)
        max_occ = max(max_occ, var_occ)
        if var_occ < min_variant_occ <= max_occ:
            break
        final_traces.append((-p, tr))
        if interrupt_simulation_when_dfg_complete and interrupt_break_condition:
            break

    # make sure that the traces are strictly ordered by their probability
    # (generally, the order is already pretty good, since the states are visited in the queue based on their order,
    # but not always 100% consistent)
    final_traces = sorted(final_traces)

    if return_variants:
        # returns the variants instead of the log
        variants = {}
        for p, tr in final_traces:
            var_occ = math.ceil(-p * max_no_variants)
            variants[tr] = var_occ

        if not (interrupted and return_only_if_complete):
            return variants
    else:
        event_log = EventLog()
        # assigns to each event an increased timestamp from 1970
        curr_timestamp = 10000000
        for index, tr in enumerate(final_traces):
            log_trace = Trace(
                attributes={xes_constants.DEFAULT_TRACEID_KEY: str(index), "probability": -tr[0]})
            for act in tr[1]:
                log_trace.append(
                    Event({activity_key: act, timestamp_key: strpfromiso.fix_naivety(datetime.datetime.fromtimestamp(curr_timestamp))}))
                # increases by 1 second
                curr_timestamp += 1
            event_log.append(log_trace)
        if not (interrupted and return_only_if_complete):
            return event_log


def get_trace_probability(trace, dfg, start_activities, end_activities, parameters=None):
    """
    Given a trace of a log, gets its probability given the complete DFG

    Parameters
    ----------------
    trace
        Trace of a log
    dfg
        *Complete* DFG
    start_activities
        Start activities of the model
    end_activities
        End activities of the model
    parameters
        Parameters of the algorithm:
        - Parameters.ACTIVITY_KEY => activity key

    Returns
    ----------------
    prob
        The probability of the trace according to the DFG
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    trace_act = tuple(x[activity_key] for x in trace)

    start_activities, node_transition_probabilities = get_node_tr_probabilities(dfg, start_activities, end_activities)

    try:
        # the following code would not crash, assuming that the trace is fully replayable on the model
        sum_prob = 0.0
        sum_prob += start_activities[trace_act[0]]

        for i in range(len(trace_act)):
            this_act = trace_act[i]
            next_act = trace_act[i + 1] if i < len(trace_act) - 1 else None
            lpt = node_transition_probabilities[this_act][next_act]

            sum_prob += lpt

        return math.exp(sum_prob)
    except:
        # if it crashes, the trace is not replayable on the model
        # then return probability 0
        return 0.0

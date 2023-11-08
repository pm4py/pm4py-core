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
import importlib.util
import random
import warnings
from enum import Enum
from typing import Optional, Dict, Any

import numpy as np

from pm4py.algo.anonymization.trace_variant_query.util import behavioralAppropriateness as ba
from pm4py.algo.anonymization.trace_variant_query.util import exp_mech as exp
from pm4py.algo.anonymization.trace_variant_query.util.util import generate_pm4py_log
from pm4py.objects.log.obj import EventLog
from pm4py.util import exec_utils

TRACE_START = "TRACE_START"
TRACE_END = "TRACE_END"
EVENT_DELIMETER = ">>>"

activityKey = 'Activity'


class Parameters(Enum):
    EPSILON = "epsilon"
    K = "k"
    P = "p"
    SHOW_PROGRESS_BAR = "show_progress_bar"


def apply(log: EventLog, parameters: Optional[Dict[Any, Any]] = None) -> EventLog:
    """
    Variant SaCoFa is described in:
    S. A. Fahrenkog-Petersen, M. Kabierski, F. Rösel, H. van der Aa and M. Weidlich, "SaCoFa: Semantics-aware
    Control-flow Anonymization for Process Mining," 2021 3rd International Conference on Process Mining (ICPM), 2021,
    pp. 72-79, doi: 10.1109/ICPM53251.2021.9576857.


    Parameters
    -------------
    log
        Event log
    parameters
        Parameters of the algorithm:
            -Parameters.EPSILON -> Strength of the differential privacy guarantee
            -Parameters.K -> Maximum prefix length of considered traces for the trace-variant-query
            -Parameters.P -> Pruning parameter of the trace-variant-query. Of a noisy trace variant, at least P traces
                            must appear. Otherwise, the trace variant and its traces won't be part of the result of the
                            trace variant query.
            -Parameters.SHOW_PROGRESS_BAR -> Enables/disables the progress bar (default: True)

    Returns
    ------------
    anonymized_trace_variant_distribution
        An anonymized trace variant distribution as an EventLog
    """

    if parameters is None:
        parameters = {}

    epsilon = exec_utils.get_param_value(Parameters.EPSILON, parameters, 1)
    k = exec_utils.get_param_value(Parameters.K, parameters, 0)
    p = exec_utils.get_param_value(Parameters.P, parameters, 1)

    if k == 0:
        warnings.warn(
            "k, the maximum prefix length of considered traces for the trace-variant-query, is set to 0, "
            "the trace-varaint-query will be empty.")
    if p == 1:
        warnings.warn("p, the pruning parameter, is set to 1, the trace-varaint-query might be very large.",
                      RuntimeWarning)

    show_progress_bar = exec_utils.get_param_value(Parameters.SHOW_PROGRESS_BAR, parameters, True)
    progress = None
    if importlib.util.find_spec("tqdm") and show_progress_bar:
        from tqdm.auto import tqdm
        progress = tqdm(total=k, desc="prefix tree construction, completed prefixes of length :: ")

    return privatize_tracevariants(log, epsilon, p, k, progress)


def privatize_tracevariants(log, epsilon, P, N, progress, smart_pruning=False, P_smart=0, sensitivity=1):
    epsilon = epsilon / sensitivity
    if not smart_pruning:
        P_smart = P
    # print("Retrieving behavioral appropriateness relations")
    traces = get_traces_from_log(log=log)
    events = get_events_from_traces(traces)
    followsRelations, precedesRelations = ba.getBARelations(traces=traces, events=events)
    events.append(
        TRACE_END)  # TRACE_END is not relevant for follows/precedes relations, but is later used to generate new prefix variants

    # print("Retrieving true prefix frequencies")
    known_prefix_frequencies = get_prefix_frequencies_from_log(log=log)

    # print("Sanitizing...")
    final_frequencies = {}
    trace_frequencies = {"": 0}
    for n in range(1, N + 1):
        # get prefix_frequencies, using either known frequency, or frequency of parent, or 0
        trace_frequencies = get_prefix_frequencies_length_n(trace_frequencies, events, n, known_prefix_frequencies)
        # exp_mech
        trace_frequencies, conformASet = privatize_trace_variants(trace_frequencies=trace_frequencies, epsilon=epsilon,
                                                                  followRelations=followsRelations,
                                                                  precedesRelations=precedesRelations, allEvents=events,
                                                                  allTraces=traces, sensitivity=sensitivity)
        # prune
        if n < N:
            trace_frequencies = prune_trace_frequencies(trace_frequencies, P, P_smart, conformASet)

        # add finished traces to output, remove from list, sanity checks
        new_frequencies = {}
        for entry in trace_frequencies.items():
            if TRACE_END in entry[0]:
                final_frequencies[entry[0]] = entry[1]
            elif n == N:
                final_frequencies[entry[0][:-3]] = entry[1]
            else:
                new_frequencies[entry[0]] = entry[1]
        trace_frequencies = new_frequencies

        if progress is not None:
            progress.update()
    if progress is not None:
        progress.close()
    del progress
    return generate_pm4py_log(trace_frequencies=final_frequencies)


def get_prefix_frequencies_from_log(log):
    prefix_frequencies = {}
    for trace in log:
        current_prefix = ""
        for event in trace._list:
            current_prefix = current_prefix + event._dict.get('concept:name') + EVENT_DELIMETER
            if current_prefix in prefix_frequencies:
                prefix_frequencies[current_prefix] += 1
            else:
                prefix_frequencies[current_prefix] = 1
        current_prefix = current_prefix + TRACE_END
        if current_prefix in prefix_frequencies:
            prefix_frequencies[current_prefix] += 1
        else:
            prefix_frequencies[current_prefix] = 1
    return prefix_frequencies


def get_prefix_frequencies_length_n(trace_frequencies, events, n, known_prefix_frequencies):
    prefixes_length_n = {}
    for prefix, frequency in trace_frequencies.items():
        for new_prefix in pref(prefix, events, n):
            if new_prefix in known_prefix_frequencies:
                new_frequency = known_prefix_frequencies[new_prefix]
                prefixes_length_n[new_prefix] = new_frequency
            else:
                prefixes_length_n[new_prefix] = 0
    return prefixes_length_n


def privatize_trace_variants(trace_frequencies, epsilon, followRelations, precedesRelations, allEvents, allTraces,
                             sensitivity):
    conformsToBASet = []
    violatesBASet = dict()
    firstEvents = get_first_events(
        traceSet=allTraces)  # all events which appear as the first event in a trace in the original log
    for trace_frequency in trace_frequencies.items():
        working_trace_frequency = list(filter(None, trace_frequency[0].split(EVENT_DELIMETER)))

        if len(working_trace_frequency) == 1:  # len(prefix) == 1 -> does a trace which begins with this prefix/event exist in the original log?
            if working_trace_frequency[0] in firstEvents:  # if so, this prefix conforms to BA, if not BA is violated
                conformsToBASet.append(trace_frequency[0])
            else:
                violatesBASet[trace_frequency[0]] = 1
            continue

        baViolations = ba.getBAViolations(allEvents=allEvents, followsRelations=followRelations,
                                          precedesRelations=precedesRelations, prefix=working_trace_frequency,
                                          TRACE_END=TRACE_END)
        if baViolations == 0:
            conformsToBASet.append(trace_frequency[0])
        else:
            violatesBASet[trace_frequency[0]] = baViolations

    not_to_prune_prefix = conformsToBASet.copy()

    output_universes = np.linspace(0, len(violatesBASet), num=len(violatesBASet) + 1, dtype=int)
    chosen_universe = exp.exp_mech(output_universes, epsilon)
    # print("conformsToBASet: ", len(conformsToBASet), "| violatesBASet: ", len(violatesBASet), "| chosen universe: ",
    #        chosen_universe)

    while chosen_universe > 0:
        for x in random.sample(list(violatesBASet.keys()), 1):
            chosen_universe = chosen_universe - min(violatesBASet[x], sensitivity)
            conformsToBASet.append(x)
            violatesBASet.pop(x)
    return apply_laplace_noise_tf(trace_frequencies, conformsToBASet, epsilon), not_to_prune_prefix


def get_first_events(traceSet):
    firstEvents = list()
    for trace in traceSet:
        if trace[0] not in firstEvents:
            firstEvents.append(trace[0])

    return firstEvents


def get_traces_from_log(log):
    logStringList = list()
    i = 0
    for trace in log:
        logStringList.append(list())
        for event in trace._list:
            logStringList[i].append(event._dict.get('concept:name'))
        i += 1
    return logStringList


def get_events_from_traces(traceSet):
    events = list()
    for t in traceSet:
        for e in t:
            if e not in events:
                events.append(e)

    return events


def prune_trace_frequencies(trace_frequencies, P, P_smart, conformSet):
    pruned_frequencies = {}
    for entry in trace_frequencies.items():
        if entry[0] in conformSet:
            if entry[1] >= P_smart or TRACE_END in entry[0]:
                pruned_frequencies[entry[0]] = entry[1]
        else:
            if entry[1] >= P or TRACE_END in entry[0]:
                pruned_frequencies[entry[0]] = entry[1]
    return pruned_frequencies


def pref(prefix, events, n):
    prefixes_length_n = []
    if not TRACE_END in prefix:
        for event in events:
            if event == TRACE_END:
                current_prefix = prefix + event
            else:
                current_prefix = prefix + event + EVENT_DELIMETER
            prefixes_length_n.append(current_prefix)
    return prefixes_length_n


def apply_laplace_noise_tf(trace_frequencies, conformsToBASet, epsilon):
    scale = 1 / epsilon
    for trace_frequency in conformsToBASet:
        noise = int(np.random.laplace(0, scale))
        trace_frequencies[trace_frequency] = trace_frequencies[trace_frequency] + noise
        if trace_frequencies[trace_frequency] < 0:
            trace_frequencies[trace_frequency] = 0
    return trace_frequencies

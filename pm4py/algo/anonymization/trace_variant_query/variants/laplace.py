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
import warnings
from enum import Enum
from typing import Optional, Dict, Any, Union

import numpy as np

from pm4py.algo.anonymization.trace_variant_query.util.util import generate_pm4py_log
from pm4py.objects.log.obj import EventLog
from pm4py.util import exec_utils

TRACE_START = "TRACE_START"
TRACE_END = "TRACE_END"
EVENT_DELIMETER = ">>>"


class Parameters(Enum):
    EPSILON = "epsilon"
    K = "k"
    P = "p"
    SHOW_PROGRESS_BAR = "show_progress_bar"


def apply(log: EventLog, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> EventLog:
    """
    Variant Laplace is described in:
    Mannhardt, F., Koschmider, A., Baracaldo, N. et al. Privacy-Preserving Process Mining. Bus Inf Syst Eng 61,
    595–614 (2019). https://doi.org/10.1007/s12599-019-00613-3

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
            "k, the maximum prefix length of considered traces for the trace-variant-query, is set to 0, the trace-varaint-query will be empty.")
    if p == 1:
        warnings.warn("p, the pruning parameter, is set to 1, the trace-varaint-query might be very large.",
                      RuntimeWarning)

    show_progress_bar = exec_utils.get_param_value(Parameters.SHOW_PROGRESS_BAR, parameters, True)
    progress = None
    if importlib.util.find_loader("tqdm") and show_progress_bar:
        from tqdm.auto import tqdm
        progress = tqdm(total=k, desc="prefix tree construction, completed prefixes of length :: ")

    return privatize_tracevariants(log, epsilon, p, k, progress)


def privatize_tracevariants(log, epsilon, p, n, progress):
    # transform log into event view and get prefix frequencies
    event_int_mapping = create_event_int_mapping(log)
    known_prefix_frequencies = get_prefix_frequencies_from_log(log)
    events = list(event_int_mapping.keys())
    events.remove(TRACE_START)

    final_frequencies = {}
    trace_frequencies = {"": 0}
    for i in range(1, n + 1):
        # get prefix_frequencies, using either known frequency, or frequency of parent, or 0
        trace_frequencies = get_prefix_frequencies_length_n(trace_frequencies, events, i, known_prefix_frequencies)
        # laplace_mechanism
        trace_frequencies = apply_laplace_noise_tf(trace_frequencies, epsilon)

        # prune
        trace_frequencies = prune_trace_frequencies(trace_frequencies, p)
        # print(trace_frequencies)
        # add finished traces to output, remove from list, sanity checks
        new_frequencies = {}
        for entry in trace_frequencies.items():
            if TRACE_END in entry[0]:
                final_frequencies[entry[0]] = entry[1]
            else:
                new_frequencies[entry[0]] = entry[1]
        trace_frequencies = new_frequencies
        # print(trace_frequencies)
        if progress is not None:
            progress.update()
    if progress is not None:
        progress.close()
    del progress
    return generate_pm4py_log(final_frequencies)


def create_event_int_mapping(log):
    event_name_list = []
    for trace in log:
        for event in trace:
            event_name = event["concept:name"]
            if not str(event_name) in event_name_list:
                event_name_list.append(event_name)
    event_int_mapping = {}
    event_int_mapping[TRACE_START] = 0
    current_int = 1
    for event_name in event_name_list:
        event_int_mapping[event_name] = current_int
        current_int = current_int + 1
    event_int_mapping[TRACE_END] = current_int
    return event_int_mapping


def get_prefix_frequencies_from_log(log):
    prefix_frequencies = {}
    for trace in log:
        current_prefix = ""
        for event in trace:
            current_prefix = current_prefix + event["concept:name"] + EVENT_DELIMETER
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
        for new_prefix in pref(prefix, events):
            if new_prefix in known_prefix_frequencies:
                new_frequency = known_prefix_frequencies[new_prefix]
                prefixes_length_n[new_prefix] = new_frequency
            else:
                prefixes_length_n[new_prefix] = 0
    return prefixes_length_n


def prune_trace_frequencies(trace_frequencies, P):
    pruned_frequencies = {}
    for entry in trace_frequencies.items():
        if entry[1] >= P:
            pruned_frequencies[entry[0]] = entry[1]
    return pruned_frequencies


def pref(prefix, events):
    prefixes_length_n = []
    if not TRACE_END in prefix:
        for event in events:
            if event == TRACE_END:
                current_prefix = prefix + event
            else:
                current_prefix = prefix + event + EVENT_DELIMETER
            prefixes_length_n.append(current_prefix)
    return prefixes_length_n


def apply_laplace_noise_tf(trace_frequencies, epsilon):
    scale = 1 / epsilon
    for trace_frequency in trace_frequencies:
        noise = int(np.random.laplace(0, scale))
        trace_frequencies[trace_frequency] = trace_frequencies[trace_frequency] + noise
        if trace_frequencies[trace_frequency] < 0:
            trace_frequencies[trace_frequency] = 0
    return trace_frequencies

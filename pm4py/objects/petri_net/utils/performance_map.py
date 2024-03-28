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
from statistics import stdev

from pm4py.objects.petri_net import semantics
from pm4py.objects.petri_net.obj import PetriNet
from pm4py.util.vis_utils import human_readable_stat, get_arc_penwidth, get_trans_freq_color
from statistics import median, mean
from pm4py.objects.log.obj import EventLog
from pm4py.util.business_hours import BusinessHours
from pm4py.util import constants

MAX_NO_THREADS = 1000


def calculate_annotation_for_trace(trace, net, initial_marking, act_trans, activity_key, ht_perf_method="last"):
    """
    Calculate annotation for a trace in the variant, in order to retrieve information
    useful for calculate frequency/performance for all the traces belonging to the variant

    Parameters
    -----------
    trace
        Trace
    net
        Petri net
    initial_marking
        Initial marking
    act_trans
        Activated transitions during token replay of the given trace
    activity_key
        Attribute that identifies the activity (must be specified if different from concept:name)
    ht_perf_method
        Method to use in order to annotate hidden transitions (performance value could be put on the last possible
        point (last) or in the first possible point (first)

    Returns
    ----------
    annotation
        Statistics annotation for the given trace
    """
    annotations_places_trans = {}
    annotations_arcs = {}
    trace_place_stats = {}
    current_trace_index = 0
    j = 0
    marking = copy(initial_marking)
    for place in marking:
        if place not in annotations_places_trans:
            annotations_places_trans[place] = {"count": 0}
            annotations_places_trans[place]["count"] = annotations_places_trans[place]["count"] + marking[place]
        trace_place_stats[place] = [current_trace_index] * marking[place]

    for z in range(len(act_trans)):
        enabled_trans_in_marking = semantics.enabled_transitions(net, marking)
        # print("enabled_trans_in_marking", enabled_trans_in_marking)

        for trans in enabled_trans_in_marking:
            if trans not in annotations_places_trans:
                annotations_places_trans[trans] = {"count": 0, "performance": [], "no_of_times_enabled": 0,
                                                   "no_of_times_activated": 0}
            annotations_places_trans[trans]["no_of_times_enabled"] = annotations_places_trans[trans][
                                                                         "no_of_times_enabled"] + 1

        trans = act_trans[z]
        if trans not in annotations_places_trans:
            annotations_places_trans[trans] = {"count": 0, "performance": [], "no_of_times_enabled": 0,
                                               "no_of_times_activated": 0}
        annotations_places_trans[trans]["count"] = annotations_places_trans[trans]["count"] + 1
        if trans not in enabled_trans_in_marking:
            annotations_places_trans[trans]["no_of_times_enabled"] = annotations_places_trans[trans][
                                                                         "no_of_times_enabled"] + 1
        annotations_places_trans[trans]["no_of_times_activated"] = annotations_places_trans[trans][
                                                                       "no_of_times_activated"] + 1

        new_marking = semantics.weak_execute(trans, marking)
        if not new_marking:
            break
        marking_diff = set(new_marking).difference(set(marking))
        for place in marking_diff:
            if place not in annotations_places_trans:
                annotations_places_trans[place] = {"count": 0}
                annotations_places_trans[place]["count"] = annotations_places_trans[place]["count"] + max(
                    new_marking[place] - marking[place], 1)
        marking = new_marking
        if j < len(trace):
            current_trace_index = j
            if trans.label == trace[j][activity_key]:
                j = j + 1

        in_arc_indexes = [trace_place_stats[arc.source][0] for arc in trans.in_arcs if
                          arc.source in trace_place_stats and trace_place_stats[arc.source]]
        if in_arc_indexes:
            min_in_arc_indexes = min(in_arc_indexes)
            max_in_arc_indexes = max(in_arc_indexes)
        else:
            min_in_arc_indexes = None
            max_in_arc_indexes = None
        performance_for_this_trans_execution = []

        for arc in trans.in_arcs:
            source_place = arc.source
            if arc not in annotations_arcs:
                annotations_arcs[arc] = {"performance": [], "count": 0}
            annotations_arcs[arc]["count"] = annotations_arcs[arc]["count"] + 1
            if source_place in trace_place_stats and trace_place_stats[source_place]:
                if trans.label or ht_perf_method == "first":
                    annotations_arcs[arc]["performance"].append(
                        [current_trace_index, trace_place_stats[source_place][0]])
                    performance_for_this_trans_execution.append(
                        [[current_trace_index, trace_place_stats[source_place][0]],
                         current_trace_index - trace_place_stats[source_place][0]])
                elif min_in_arc_indexes:
                    annotations_arcs[arc]["performance"].append([current_trace_index, current_trace_index])
                    performance_for_this_trans_execution.append([[current_trace_index, current_trace_index], 0])

                del trace_place_stats[source_place][0]
        for arc in trans.out_arcs:
            target_place = arc.target
            if arc not in annotations_arcs:
                annotations_arcs[arc] = {"performance": [], "count": 0}
            annotations_arcs[arc]["count"] = annotations_arcs[arc]["count"] + 1
            if target_place not in trace_place_stats:
                trace_place_stats[target_place] = []

            if trans.label or ht_perf_method == "first":
                trace_place_stats[target_place].append(current_trace_index)
            elif max_in_arc_indexes:
                trace_place_stats[target_place].append(max_in_arc_indexes)

        if performance_for_this_trans_execution:
            performance_for_this_trans_execution = sorted(performance_for_this_trans_execution, key=lambda x: x[1])

            annotations_places_trans[trans]["performance"].append(performance_for_this_trans_execution[0][0])

    return annotations_places_trans, annotations_arcs


def single_element_statistics(log, net, initial_marking, aligned_traces, variants_idx, activity_key="concept:name",
                              timestamp_key="time:timestamp", ht_perf_method="last", parameters=None):
    """
    Get single Petrinet element statistics

    Parameters
    ------------
    log
        Log
    net
        Petri net
    initial_marking
        Initial marking
    aligned_traces
        Result of the token-based replay
    variants_idx
        Variants along with indexes of belonging traces
    activity_key
        Activity key (must be specified if different from concept:name)
    timestamp_key
        Timestamp key (must be specified if different from time:timestamp)
    ht_perf_method
        Method to use in order to annotate hidden transitions (performance value could be put on the last possible
        point (last) or in the first possible point (first)
    parameters
        Possible parameters of the algorithm

    Returns
    ------------
    statistics
        Petri net element statistics (frequency, unaggregated performance)
    """
    if parameters is None:
        parameters = {}

    from pm4py.objects.conversion.log import converter as log_converter
    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    business_hours = parameters["business_hours"] if "business_hours" in parameters else False
    business_hours_slots = parameters["business_hour_slots"] if "business_hour_slots" in parameters else constants.DEFAULT_BUSINESS_HOUR_SLOTS
    count_once_per_trace = parameters["count_once_per_trace"] if "count_once_per_trace" in parameters else False

    statistics = {}

    for variant in variants_idx:
        first_trace = log[variants_idx[variant][0]]
        act_trans0 = aligned_traces[variants_idx[variant][0]]["activated_transitions"]
        act_trans = []
        if count_once_per_trace:
            for t in act_trans0:
                if t not in act_trans:
                    act_trans.append(t)
        else:
            act_trans = act_trans0
        annotations_places_trans, annotations_arcs = calculate_annotation_for_trace(first_trace, net, initial_marking,
                                                                                    act_trans, activity_key,
                                                                                    ht_perf_method=ht_perf_method)

        for el in annotations_places_trans:
            if el not in statistics:
                statistics[el] = {"count": 0, "performance": [], "log_idx": [], "no_of_times_enabled": 0,
                                  "no_of_times_activated": 0}
            statistics[el]["count"] += annotations_places_trans[el]["count"] * len(variants_idx[variant])
            if "no_of_times_enabled" in annotations_places_trans[el]:
                statistics[el]["no_of_times_enabled"] += annotations_places_trans[el]["no_of_times_enabled"] * len(
                    variants_idx[variant])
                statistics[el]["no_of_times_activated"] += annotations_places_trans[el]["no_of_times_activated"] * len(
                    variants_idx[variant])

            if "performance" in annotations_places_trans[el]:
                for trace_idx in variants_idx[variant]:
                    trace = log[trace_idx]
                    for perf_couple in annotations_places_trans[el]["performance"]:
                        if timestamp_key in trace[perf_couple[0]] and timestamp_key in trace[perf_couple[1]]:
                            if business_hours:
                                bh = BusinessHours(trace[perf_couple[1]][timestamp_key],
                                                   trace[perf_couple[0]][timestamp_key],
                                                   business_hour_slots=business_hours_slots)
                                perf = bh.get_seconds()
                            else:
                                perf = (trace[perf_couple[0]][timestamp_key] - trace[perf_couple[1]][
                                    timestamp_key]).total_seconds()
                        else:
                            perf = 0.0
                        statistics[el]["performance"].append(perf)
                        statistics[el]["log_idx"].append(trace_idx)
        for el in annotations_arcs:
            if el not in statistics:
                statistics[el] = {"count": 0, "performance": []}
            statistics[el]["count"] += annotations_arcs[el]["count"] * len(variants_idx[variant])
            for trace_idx in variants_idx[variant]:
                trace = log[trace_idx]
                for perf_couple in annotations_arcs[el]["performance"]:
                    if timestamp_key in trace[perf_couple[0]] and timestamp_key in trace[perf_couple[1]]:
                        if business_hours:
                            bh = BusinessHours(trace[perf_couple[1]][timestamp_key],
                                               trace[perf_couple[0]][timestamp_key],
                                               business_hour_slots=business_hours_slots)
                            perf = bh.get_seconds()
                        else:
                            perf = (trace[perf_couple[0]][timestamp_key] - trace[perf_couple[1]][
                                timestamp_key]).total_seconds()
                    else:
                        perf = 0.0
                    statistics[el]["performance"].append(perf)

    return statistics


def find_min_max_trans_frequency(statistics):
    """
    Find minimum and maximum transition frequency

    Parameters
    -----------
    statistics
        Element statistics

    Returns
    ----------
    min_frequency
        Minimum transition frequency (in the replay)
    max_frequency
        Maximum transition frequency (in the replay)
    """
    min_frequency = 9999999999
    max_frequency = 0
    for elem in statistics.keys():
        if type(elem) is PetriNet.Transition:
            if statistics[elem]["count"] < min_frequency:
                min_frequency = statistics[elem]["count"]
            if statistics[elem]["count"] > max_frequency:
                max_frequency = statistics[elem]["count"]
    return min_frequency, max_frequency


def find_min_max_arc_frequency(statistics):
    """
    Find minimum and maximum arc frequency

    Parameters
    -----------
    statistics
        Element statistics

    Returns
    -----------
    min_frequency
        Minimum arc frequency
    max_frequency
        Maximum arc frequency
    """
    min_frequency = 9999999999
    max_frequency = 0
    for elem in statistics.keys():
        if type(elem) is PetriNet.Arc:
            if statistics[elem]["count"] < min_frequency:
                min_frequency = statistics[elem]["count"]
            if statistics[elem]["count"] > max_frequency:
                max_frequency = statistics[elem]["count"]
    return min_frequency, max_frequency


def aggregate_stats(statistics, elem, aggregation_measure):
    """
    Aggregate the statistics

    Parameters
    -----------
    statistics
        Element statistics
    elem
        Current element
    aggregation_measure
        Aggregation measure (e.g. mean, min) to use

    Returns
    -----------
    aggr_stat
        Aggregated statistics
    """
    aggr_stat = 0
    if aggregation_measure == "mean" or aggregation_measure is None:
        aggr_stat = mean(statistics[elem]["performance"])
    elif aggregation_measure == "median":
        aggr_stat = median(statistics[elem]["performance"])
    elif aggregation_measure == "stdev":
        aggr_stat = stdev(statistics[elem]["performance"])
    elif aggregation_measure == "sum":
        aggr_stat = sum(statistics[elem]["performance"])
    elif aggregation_measure == "min":
        aggr_stat = min(statistics[elem]["performance"])
    elif aggregation_measure == "max":
        aggr_stat = max(statistics[elem]["performance"])

    return aggr_stat


def find_min_max_arc_performance(statistics, aggregation_measure):
    """
    Find minimum and maximum arc performance

    Parameters
    -----------
    statistics
        Element statistics
    aggregation_measure
        Aggregation measure (e.g. mean, min) to use

    Returns
    -----------
    min_performance
        Minimum performance
    max_performance
        Maximum performance
    """
    min_performance = 9999999999
    max_performance = 0
    for elem in statistics.keys():
        if type(elem) is PetriNet.Arc:
            if statistics[elem]["performance"]:
                aggr_stat = aggregate_stats(statistics, elem, aggregation_measure)
                if aggr_stat < min_performance:
                    min_performance = aggr_stat
                if aggr_stat > max_performance:
                    max_performance = aggr_stat
    return min_performance, max_performance


def aggregate_statistics(statistics, measure="frequency", aggregation_measure=None,
                         stat_locale: dict = {}):
    """
    Gets aggregated statistics

    Parameters
    ----------
    statistics
        Individual element statistics (including unaggregated performances)
    measure
        Desidered view on data (frequency or performance)
    aggregation_measure
        Aggregation measure (e.g. mean, min) to use
    stat_locale
        Dict to locale the stat strings
    
    Returns
    ----------
    aggregated_statistics
        Aggregated statistics for arcs, transitions, places
    """
    min_trans_frequency, max_trans_frequency = find_min_max_trans_frequency(statistics)
    min_arc_frequency, max_arc_frequency = find_min_max_arc_frequency(statistics)
    min_arc_performance, max_arc_performance = find_min_max_arc_performance(statistics, aggregation_measure)
    aggregated_statistics = {}
    for elem in statistics.keys():
        if type(elem) is PetriNet.Arc:
            if measure == "frequency":
                freq = statistics[elem]["count"]
                arc_penwidth = get_arc_penwidth(freq, min_arc_frequency, max_arc_frequency)
                aggregated_statistics[elem] = {"label": str(freq), "penwidth": str(arc_penwidth)}
            elif measure == "performance":
                if statistics[elem]["performance"]:
                    aggr_stat = aggregate_stats(statistics, elem, aggregation_measure)
                    aggr_stat_hr = human_readable_stat(aggr_stat, stat_locale)
                    arc_penwidth = get_arc_penwidth(aggr_stat, min_arc_performance, max_arc_performance)
                    aggregated_statistics[elem] = {"label": aggr_stat_hr, "penwidth": str(arc_penwidth)}
        elif type(elem) is PetriNet.Transition:
            if measure == "frequency":
                if elem.label is not None:
                    freq = statistics[elem]["count"]
                    color = get_trans_freq_color(freq, min_trans_frequency, max_trans_frequency)
                    aggregated_statistics[elem] = {"label": elem.label + " (" + str(freq) + ")", "color": color}
        elif type(elem) is PetriNet.Place:
            pass
    return aggregated_statistics


def get_transition_performance_with_token_replay(log, net, im, fm):
    """
    Gets the transition performance through the usage of token-based replay

    Parameters
    -------------
    log
        Event log
    net
        Petri net
    im
        Initial marking
    fm
        Final marking

    Returns
    --------------
    transition_performance
        Dictionary where each transition label is associated to performance measures
    """
    from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
    from pm4py.statistics.variants.log import get as variants_get

    variants_idx = variants_get.get_variants_from_log_trace_idx(log)
    aligned_traces = token_replay.apply(log, net, im, fm)
    element_statistics = single_element_statistics(log, net, im,
                                                                   aligned_traces, variants_idx)

    transition_performance = {}
    for el in element_statistics:
        if type(el) is PetriNet.Transition and el.label is not None:
            if "log_idx" in element_statistics[el] and "performance" in element_statistics[el]:
                if len(element_statistics[el]["performance"]) > 0:
                    transition_performance[str(el)] = {"all_values": [], "case_association": {}, "mean": 0.0,
                                                       "median": 0.0}
                    for i in range(len(element_statistics[el]["log_idx"])):
                        if not element_statistics[el]["log_idx"][i] in transition_performance[str(el)][
                            "case_association"]:
                            transition_performance[str(el)]["case_association"][
                                element_statistics[el]["log_idx"][i]] = []
                        transition_performance[str(el)]["case_association"][
                            element_statistics[el]["log_idx"][i]].append(
                            element_statistics[el]["performance"][i])
                        transition_performance[str(el)]["all_values"].append(element_statistics[el]["performance"][i])
                    transition_performance[str(el)]["all_values"] = sorted(
                        transition_performance[str(el)]["all_values"])
                    if transition_performance[str(el)]["all_values"]:
                        transition_performance[str(el)]["mean"] = mean(transition_performance[str(el)]["all_values"])
                        transition_performance[str(el)]["median"] = median(
                            transition_performance[str(el)]["all_values"])
    return transition_performance


def get_idx_exceeding_specified_acti_performance(log, transition_performance, activity, lower_bound):
    """
    Get indexes of the cases exceeding the specified activity performance threshold

    Parameters
    ------------
    log
        Event log
    transition_performance
        Dictionary where each transition label is associated to performance measures
    activity
        Target activity (of the filter)
    lower_bound
        Lower bound (filter cases which have a duration of the activity exceeding)

    Returns
    ------------
    idx
        A list of indexes in the log
    """
    satisfying_indexes = sorted(list(set(
        x for x, y in transition_performance[activity]["case_association"].items() if max(y) >= lower_bound)))
    return satisfying_indexes


def filter_cases_exceeding_specified_acti_performance(log, transition_performance, activity, lower_bound):
    """
    Filter cases exceeding the specified activity performance threshold

    Parameters
    ------------
    log
        Event log
    transition_performance
        Dictionary where each transition label is associated to performance measures
    activity
        Target activity (of the filter)
    lower_bound
        Lower bound (filter cases which have a duration of the activity exceeding)

    Returns
    ------------
    filtered_log
        Filtered log
    """
    satisfying_indexes = get_idx_exceeding_specified_acti_performance(log, transition_performance, activity,
                                                                      lower_bound)
    new_log = EventLog(list(log[i] for i in satisfying_indexes))
    return new_log

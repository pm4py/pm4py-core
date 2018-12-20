from copy import copy
from statistics import mean, median, stdev

from pm4py.objects.petri import semantics
from pm4py.objects.petri.petrinet import PetriNet
from pm4py.visualization.common.utils import *

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
                              timestamp_key="time:timestamp", ht_perf_method="last"):
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

    Returns
    ------------
    statistics
        Petri net element statistics (frequency, unaggregated performance)
    """

    statistics = {}

    for variant in variants_idx:
        first_trace = log[variants_idx[variant][0]]
        act_trans = aligned_traces[variants_idx[variant][0]]["activated_transitions"]
        annotations_places_trans, annotations_arcs = calculate_annotation_for_trace(first_trace, net, initial_marking,
                                                                                    act_trans, activity_key,
                                                                                    ht_perf_method=ht_perf_method)

        for el in annotations_places_trans:
            if el not in statistics:
                statistics[el] = {"count": 0, "performance": [], "no_of_times_enabled": 0, "no_of_times_activated": 0}
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
                        perf = (trace[perf_couple[0]][timestamp_key] - trace[perf_couple[1]][
                            timestamp_key]).total_seconds()
                        statistics[el]["performance"].append(perf)
        for el in annotations_arcs:
            if el not in statistics:
                statistics[el] = {"count": 0, "performance": []}
            statistics[el]["count"] += annotations_arcs[el]["count"] * len(variants_idx[variant])
            for trace_idx in variants_idx[variant]:
                trace = log[trace_idx]
                for perf_couple in annotations_arcs[el]["performance"]:
                    perf = (trace[perf_couple[0]][timestamp_key] - trace[perf_couple[1]][timestamp_key]).total_seconds()
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


def aggregate_statistics(statistics, measure="frequency", aggregation_measure=None):
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
                    aggr_stat_hr = human_readable_stat(aggr_stat)
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

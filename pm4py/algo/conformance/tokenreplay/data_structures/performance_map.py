from copy import copy
from pm4py.entities.petri import semantics
from pm4py.entities.petri.petrinet import PetriNet
from statistics import mean, median, stdev
from threading import Lock, Thread
from pm4py.visualization.common.utils import *

MAX_NO_THREADS = 1000

def calculate_annotation_for_trace(trace, net, initial_marking, actTrans, activity_key):
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
    actTrans
        Activated transitions during token replay of the given trace
    activity_key
        Attribute that identifies the activity (must be specified if different from concept:name)

    Returns
    ----------
    annotation
        Statistics annotation for the given trace
    """
    annotations_placesTrans = {}
    annotations_arcs = {}
    tracePlaceStats = {}
    currentTraceIndex = 0
    j = 0
    marking = copy(initial_marking)
    for place in marking:
        if not place in annotations_placesTrans:
            annotations_placesTrans[place] = {"count":0}
            annotations_placesTrans[place]["count"] = annotations_placesTrans[place]["count"] + marking[place]
        tracePlaceStats[place] = [currentTraceIndex] * marking[place]
    z = 0
    while z < len(actTrans):
        trans = actTrans[z]
        if not trans in annotations_placesTrans:
            annotations_placesTrans[trans] = {"count": 0}
            annotations_placesTrans[trans]["count"] = annotations_placesTrans[trans]["count"] + 1

        new_marking = semantics.weak_execute(trans, net, marking)
        if not new_marking:
            break
        marking_diff = set(new_marking).difference(set(marking))
        for place in marking_diff:
            if not place in annotations_placesTrans:
                annotations_placesTrans[place] = {"count": 0}
                annotations_placesTrans[place]["count"] = annotations_placesTrans[place]["count"] + max(new_marking[place] - marking[place], 1)
        marking = new_marking
        if j < len(trace):
            currentTraceIndex = j
            if trans.label == trace[j][activity_key]:
                j = j + 1
        for arc in trans.in_arcs:
            sourcePlace = arc.source
            if not arc in annotations_arcs:
                annotations_arcs[arc] = {"performance": [], "count": 0}
                annotations_arcs[arc]["count"] = annotations_arcs[arc]["count"] + 1
            if sourcePlace in tracePlaceStats and tracePlaceStats[sourcePlace]:
                annotations_arcs[arc]["performance"].append([currentTraceIndex, tracePlaceStats[sourcePlace][0]])
                del tracePlaceStats[sourcePlace][0]
        for arc in trans.out_arcs:
            targetPlace = arc.target
            if not arc in annotations_arcs:
                annotations_arcs[arc] = {"performance": [], "count": 0}
                annotations_arcs[arc]["count"] = annotations_arcs[arc]["count"] + 1
            if not targetPlace in tracePlaceStats:
                tracePlaceStats[targetPlace] = []
            tracePlaceStats[targetPlace].append(currentTraceIndex)
        z = z + 1

    return annotations_placesTrans, annotations_arcs

def single_element_statistics(log, net, initial_marking, aligned_traces, variants_idx, activity_key="concept:name", timestamp_key="time:timestamp"):
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

    Returns
    ------------
    statistics
        Petri net element statistics (frequency, unaggregated performance)
    """

    statistics = {}

    for variant in variants_idx:
        first_trace = log[variants_idx[variant][0]]
        actTrans = aligned_traces[variants_idx[variant][0]]["actTrans"]
        annotations_placesTrans, annotations_arcs = calculate_annotation_for_trace(first_trace, net, initial_marking, actTrans, activity_key)

        for el in annotations_placesTrans:
            if not el in statistics:
                statistics[el] = {"count": 0}
            statistics[el]["count"] += annotations_placesTrans[el]["count"] * len(variants_idx[variant])

        for el in annotations_arcs:
            if not el in statistics:
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

def aggregate_stats(statistics, elem, aggregationMeasure):
    """
    Aggregate the statistics

    Parameters
    -----------
    statistics
        Element statistics
    elem
        Current element

    Returns
    -----------
    aggr_stat
        Aggregated statistics
    """
    if aggregationMeasure == "mean" or aggregationMeasure is None:
        aggr_stat = mean(statistics[elem]["performance"])
    elif aggregationMeasure == "median":
        aggr_stat = median(statistics[elem]["performance"])
    elif aggregationMeasure == "stdev":
        aggr_stat = stdev(statistics[elem]["performance"])
    elif aggregationMeasure == "sum":
        aggr_stat = sum(statistics[elem]["performance"])
    elif aggregationMeasure == "min":
        aggr_stat = min(statistics[elem]["performance"])
    elif aggregationMeasure == "max":
        aggr_stat = max(statistics[elem]["performance"])

    return aggr_stat

def find_min_max_arc_performance(statistics, aggregationMeasure):
    """
    Find minimum and maximum arc performance

    Parameters
    -----------
    statistics
        Element statistics

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
                aggr_stat = aggregate_stats(statistics, elem, aggregationMeasure)
                if aggr_stat < min_performance:
                    min_performance = aggr_stat
                if aggr_stat > max_performance:
                    max_performance = aggr_stat
    return min_performance, max_performance

def aggregate_statistics(statistics, measure="frequency", aggregationMeasure=None):
    """
    Gets aggregated statistics

    Parameters
    ----------
    statistics
        Individual element statistics (including unaggregated performances)

    Returns
    ----------
    aggregated_statistics
        Aggregated statistics for arcs, transitions, places
    """
    min_trans_frequency, max_trans_frequency = find_min_max_trans_frequency(statistics)
    min_arc_frequency, max_arc_frequency = find_min_max_arc_frequency(statistics)
    min_arc_performance, max_arc_performance = find_min_max_arc_performance(statistics, aggregationMeasure)
    aggregated_statistics = {}
    for elem in statistics.keys():
        if type(elem) is PetriNet.Arc:
            if measure == "frequency":
                freq = statistics[elem]["count"]
                arc_penwidth = get_arc_penwidth(freq, min_arc_frequency, max_arc_frequency)
                aggregated_statistics[elem] = {"label":str(freq),"penwidth":str(arc_penwidth)}
            elif measure == "performance":
                if statistics[elem]["performance"]:
                    aggr_stat = aggregate_stats(statistics, elem, aggregationMeasure)
                    aggr_stat_hr = human_readable_stat(aggr_stat)
                    arc_penwidth = get_arc_penwidth(aggr_stat, min_arc_performance, max_arc_performance)
                    aggregated_statistics[elem] = {"label":aggr_stat_hr,"penwidth":str(arc_penwidth)}
        elif type(elem) is PetriNet.Transition:
            if measure == "frequency":
                if elem.label is not None:
                    freq = statistics[elem]["count"]
                    color = get_trans_freq_color(freq, min_trans_frequency, max_trans_frequency)
                    aggregated_statistics[elem] = {"label":elem.label+" ("+str(freq)+")", "color": color}
        elif type(elem) is PetriNet.Place:
            pass
    return aggregated_statistics
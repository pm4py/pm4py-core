from statistics import mean, median, stdev

from pm4py.visualization.common.utils import *


def get_shortest_paths_from_trans(original_trans, spaths):
    """
    Get arcs that are shortest paths between a given
    visible transition and other visible transitions

    Parameters
    -----------
    original_trans
        Original transition
    spaths
        Current dictionary of shortest paths

    Returns
    -----------
    spaths
        Updated shortest paths
    """
    already_visited_arcs = []
    already_visited_trans = []
    already_visited_places = []
    trans_list = [original_trans]
    for i in range(10000000):
        if not trans_list:
            break
        trans = trans_list.pop(0)
        already_visited_trans.append(trans)
        for out_arc in trans.out_arcs:
            if out_arc not in already_visited_arcs:
                already_visited_arcs.append(out_arc)
                target_place = out_arc.target
                if target_place not in already_visited_places:
                    already_visited_places.append(target_place)
                    for place_out_arc in target_place.out_arcs:
                        if place_out_arc not in already_visited_places:
                            target_trans = place_out_arc.target
                            if target_trans not in already_visited_trans or target_trans == original_trans:
                                already_visited_trans.append(target_trans)
                                if target_trans.label:
                                    if out_arc not in spaths:
                                        spaths[out_arc] = set()
                                    if place_out_arc not in spaths:
                                        spaths[place_out_arc] = set()
                                    spaths[out_arc].add(((original_trans.name, target_trans.name), 0))
                                    spaths[place_out_arc].add(((original_trans.name, target_trans.name), 1))
                                trans_list.append(target_trans)
    return spaths


def get_shortest_paths(net):
    """
    Gets shortest paths between visible transitions in a Petri net

    Parameters
    -----------
    net
        Petri net

    Returns
    -----------
    spaths
        Shortest paths
    """
    spaths = {}
    for trans in net.transitions:
        if trans.label:
            spaths = get_shortest_paths_from_trans(trans, spaths)
    return spaths


def get_decorations_from_dfg_spaths_acticount(net, dfg, spaths, activities_count, variant="frequency",
                                              aggregation_measure=None):
    """
    Get decorations from Petrinet without doing any replay
    but based on DFG measures, shortest paths and activities count.
    The variant could be 'frequency' or 'performance'.
    Aggregation measure could also be specified

    Parameters
    -----------
    net
        Petri net
    dfg
        Directly-Follows graph
    spaths
        Shortest paths between visible transitions in the Petri net
    activities_count
        Count of activities in the Petri net
    variant
        Describe how to decorate the Petri net (could be frequency or performance)
    aggregation_measure
        Specifies the aggregation measure

    Returns
    -----------
    decorations
        Decorations to use for the Petri net
    """
    decorations_single_contrib = {}
    decorations_int = {}
    decorations = {}
    if aggregation_measure is None:
        if "frequency" in variant:
            aggregation_measure = "sum"
        elif "performance" in variant:
            aggregation_measure = "mean"
    for arc in spaths:
        for couple in spaths[arc]:
            dfg_key = couple[0]
            if dfg_key in dfg:
                if arc not in decorations_single_contrib:
                    decorations_single_contrib[arc] = []
                decorations_single_contrib[arc].append(dfg[dfg_key])
    for arc in decorations_single_contrib:
        if aggregation_measure == "sum":
            decorations_int[arc] = sum(decorations_single_contrib[arc])
        elif aggregation_measure == "mean":
            decorations_int[arc] = mean(decorations_single_contrib[arc])
        elif aggregation_measure == "median":
            decorations_int[arc] = median(decorations_single_contrib[arc])
        elif aggregation_measure == "stdev":
            decorations_int[arc] = stdev(decorations_single_contrib[arc])
        elif aggregation_measure == "min":
            decorations_int[arc] = min(decorations_single_contrib[arc])
        elif aggregation_measure == "max":
            decorations_int[arc] = max(decorations_single_contrib[arc])

    if decorations_int:
        arcs_min_value = min(list(decorations_int.values()))
        arcs_max_value = max(list(decorations_int.values()))
        for arc in decorations_int:
            if "performance" in variant:
                arc_label = human_readable_stat(decorations_int[arc])
            else:
                arc_label = str(decorations_int[arc])
            decorations[arc] = {"label": arc_label,
                                "penwidth": str(get_arc_penwidth(decorations_int[arc], arcs_min_value, arcs_max_value))}
        if "frequency" in variant:
            act_min_value = min(list(activities_count.values()))
            act_max_value = max(list(activities_count.values()))
            trans_map = {}
            for trans in net.transitions:
                if trans.label:
                    trans_map[trans.label] = trans
            for act in activities_count:
                if act in trans_map:
                    trans = trans_map[act]
                    color = get_trans_freq_color(activities_count[act], act_min_value, act_max_value)
                    label = act + " (" + str(activities_count[act]) + ")"
                    decorations[trans] = {"label": label, "color": color}

    return decorations

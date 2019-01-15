from statistics import mean, median, stdev

from pm4py.visualization.common.utils import *


def update_spaths_given_result(spaths, original_trans, target_trans, out_arc, place_out_arc, parent_place_out_arc,
                               visited_arcs, rec_depth):
    """
    Method that updates the shortest paths given the finding of the shortest paths function

    Parameters
    -------------
    spaths
        Arcs that are shortest paths between (visible) transitions
    original_trans
        Source transition of the shortest paths research
    target_trans
        Found target transition of the shortest paths research
    out_arc
        Arc connected to the target transition
    place_out_arc
        Arc connected to the immediately preceding place
    parent_place_out_arc
        Map of arcs connecting places
    visited_arcs
        All the visited arcs by this routine
    rec_depth
        Current recursion depth

    Returns
    --------------
    spaths
        Arcs that are shortest paths between (visible) transitions
    visited_arcs
        All the visited arcs by this routine
    """
    visited_arcs = set()
    visited_arcs.add(out_arc)
    visited_arcs.add(place_out_arc)
    el1 = ((original_trans.name, target_trans.name), 0)
    if out_arc not in spaths:
        spaths[out_arc] = set()
    if el1 not in spaths[out_arc]:
        spaths[out_arc].add(el1)
    el2 = ((original_trans.name, target_trans.name), 1)
    if place_out_arc not in spaths:
        spaths[place_out_arc] = set()
    if el2 not in spaths[place_out_arc]:
        spaths[place_out_arc].add(el2)

    """if out_arc in parent_place_out_arc:
        ppoa_set = parent_place_out_arc[out_arc]
        for ppoa in ppoa_set:
            print(ppoa)
            if ppoa not in visited_arcs:
                spaths, visited_arcs = update_spaths_given_result(spaths, original_trans, target_trans, place_out_arc,
                                                                  ppoa, parent_place_out_arc, visited_arcs,
                                                                  rec_depth + 1)"""

    return spaths, visited_arcs


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
    parent_place_out_arc = {}
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
                            if place_out_arc not in parent_place_out_arc:
                                parent_place_out_arc[place_out_arc] = set()
                            parent_place_out_arc[place_out_arc].add(out_arc)
                            target_trans = place_out_arc.target
                            if target_trans not in already_visited_trans or target_trans == original_trans:
                                already_visited_trans.append(target_trans)
                                if target_trans.label:
                                    visited_arcs = set()
                                    spaths, visited_arcs = update_spaths_given_result(spaths, original_trans,
                                                                                      target_trans,
                                                                                      out_arc,
                                                                                      place_out_arc,
                                                                                      parent_place_out_arc,
                                                                                      visited_arcs, 0)
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
    decorations_single_contrib_trans = {}
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
                if dfg_key[1] not in decorations_single_contrib_trans:
                    decorations_single_contrib_trans[dfg_key[1]] = {}
                decorations_single_contrib_trans[dfg_key[1]][dfg_key[0]] = dfg[dfg_key]
    for arc in decorations_single_contrib:
        decorations_value = None
        if aggregation_measure == "sum":
            decorations_value = sum(decorations_single_contrib[arc])
        elif aggregation_measure == "mean":
            decorations_value = mean(decorations_single_contrib[arc])
        elif aggregation_measure == "median":
            decorations_value = median(decorations_single_contrib[arc])
        elif aggregation_measure == "stdev":
            decorations_value = stdev(decorations_single_contrib[arc])
        elif aggregation_measure == "min":
            decorations_value = min(decorations_single_contrib[arc])
        elif aggregation_measure == "max":
            decorations_value = max(decorations_single_contrib[arc])
        if decorations_value is not None:
            decorations_int[arc] = decorations_value

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
        trans_map = {}
        for trans in net.transitions:
            if trans.label:
                trans_map[trans.label] = trans
        if "frequency" in variant:
            act_min_value = min(list(activities_count.values()))
            act_max_value = max(list(activities_count.values()))
            for act in activities_count:
                if act in trans_map:
                    trans = trans_map[act]
                    color = get_trans_freq_color(activities_count[act], act_min_value, act_max_value)
                    label = act + " (" + str(activities_count[act]) + ")"
                    decorations[trans] = {"label": label, "color": color}
        elif "performance" in variant:
            for act in decorations_single_contrib_trans:
                if act in trans_map:
                    trans = trans_map[act]
                    trans_values = list(decorations_single_contrib_trans[act].values())
                    decorations[trans] = {"performance": mean(trans_values)}

    return decorations

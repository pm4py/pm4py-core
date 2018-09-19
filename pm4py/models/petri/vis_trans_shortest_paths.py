from statistics import mean, median, stdev
from pm4py.visualization.common.utils import *

def get_shortest_paths_from_trans(net, original_trans, spaths):
    """
    Get arcs that are shortest paths between a given
    visible transition and other visible transitions

    Parameters
    -----------
    net
        Petri net
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
    while trans_list:
        trans = trans_list.pop(0)
        already_visited_trans.append(trans)
        for out_arc in trans.out_arcs:
            if not out_arc in already_visited_arcs:
                already_visited_arcs.append(out_arc)
                target_place = out_arc.target
                if not target_place in already_visited_places:
                    already_visited_places.append(target_place)
                    for place_out_arc in target_place.out_arcs:
                        if not place_out_arc in already_visited_places:
                            target_trans = place_out_arc.target
                            if not target_trans in already_visited_trans or target_trans == original_trans:
                                already_visited_trans.append(target_trans)
                                if target_trans.label:
                                    if not out_arc in spaths:
                                        spaths[out_arc] = set()
                                    if not place_out_arc in spaths:
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
            spaths = get_shortest_paths_from_trans(net, trans, spaths)
    return spaths

def get_net_decorations_from_dfg_spaths_acticount(net, dfg, spaths, activities_count, variant="frequency", aggregationMeasure=None):
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
    aggregationMeasure
        Specifies the aggregation measure

    Returns
    -----------
    decorations
        Decorations to use for the Petri net
    """
    decorations_single_contrib = {}
    decorations_int = {}
    decorations = {}
    if aggregationMeasure is None:
        if "frequency" in variant:
            aggregationMeasure = "sum"
        elif "performance" in variant:
            aggregationMeasure = "mean"
    for arc in spaths:
        for couple in spaths[arc]:
            dfg_key = couple[0]
            status = couple[1]
            if dfg_key in dfg:
                if not arc in decorations_single_contrib:
                    decorations_single_contrib[arc] = []
                decorations_single_contrib[arc].append(dfg[dfg_key])
    for arc in decorations_single_contrib:
        if aggregationMeasure == "sum":
            decorations_int[arc] = sum(decorations_single_contrib[arc])
        elif aggregationMeasure == "mean":
            decorations_int[arc] = mean(decorations_single_contrib[arc])
        elif aggregationMeasure == "median":
            decorations_int[arc] = median(decorations_single_contrib[arc])
        elif aggregationMeasure == "stdev":
            decorations_int[arc] = stdev(decorations_single_contrib[arc])
        elif aggregationMeasure == "min":
            decorations_int[arc] = min(decorations_single_contrib[arc])
        elif aggregationMeasure == "max":
            decorations_int[arc] = max(decorations_single_contrib[arc])

    if decorations_int:
        arcs_min_value = min(list(decorations_int.values()))
        arcs_max_value = max(list(decorations_int.values()))
        for arc in decorations_int:
            if "performance" in variant:
                arcLabel = human_readable_stat(decorations_int[arc])
            else:
                arcLabel = str(decorations_int[arc])
            decorations[arc] = {"label": arcLabel, "penwidth": str(get_arc_penwidth(decorations_int[arc], arcs_min_value, arcs_max_value))}
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
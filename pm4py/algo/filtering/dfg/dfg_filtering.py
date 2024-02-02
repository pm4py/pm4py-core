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
import math
from copy import deepcopy

from pm4py.objects.dfg.utils import dfg_utils
from pm4py.util import constants, nx_utils

DEFAULT_NOISE_THRESH_DF = 0.16


def generate_nx_graph_from_dfg(dfg, start_activities, end_activities, activities_count):
    """
    Generate a NetworkX graph for reachability-checking purposes out of the DFG

    Parameters
    --------------
    dfg
        DFG
    start_activities
        Start activities
    end_activities
        End activities
    activities_count
        Activities of the DFG along with their count

    Returns
    --------------
    G
        NetworkX digraph
    start_node
        Identifier of the start node (connected to all the start activities)
    end_node
        Identifier of the end node (connected to all the end activities)
    """
    start_node = '4d872045-8664-4e21-bd55-5da5edb096fe' # made static to avoid undeterminism
    end_node = 'b8136db7-b162-4763-bd68-4d5ccbcdff87' # made static to avoid undeterminism
    G = nx_utils.DiGraph()
    G.add_node(start_node)
    G.add_node(end_node)
    for act in activities_count:
        G.add_node(act)
    for edge in dfg:
        G.add_edge(edge[0], edge[1])
    for act in start_activities:
        G.add_edge(start_node, act)
    for act in end_activities:
        G.add_edge(act, end_node)
    return G, start_node, end_node


def filter_dfg_on_activities_percentage(dfg0, start_activities0, end_activities0, activities_count0, percentage):
    """
    Filters a DFG (complete, and so connected) on the specified percentage of activities
    (but ensuring that every node is still reachable from the start and to the end)

    Parameters
    ----------------
    dfg0
        (Complete, and so connected) DFG
    start_activities0
        Start activities
    end_activities0
        End activities
    activities_count0
        Activities of the DFG along with their count
    percentage
        Percentage of activities

    Returns
    ----------------
    dfg
        (Filtered) DFG
    start_activities
        (Filtered) start activities
    end_activities
        (Filtered) end activities
    activities_count
        (Filtered) activities of the DFG along with their count
    """
    # since the dictionaries/sets are modified, a deepcopy is the best option to ensure data integrity
    dfg = deepcopy(dfg0)
    start_activities = deepcopy(start_activities0)
    end_activities = deepcopy(end_activities0)
    activities_count = deepcopy(activities_count0)

    if len(activities_count) > 1 and len(dfg) > 1:
        activities_count_sorted_list = sorted([(x, y) for x, y in activities_count.items()], key=lambda x: (x[1], x[0]),
                                              reverse=True)
        # retrieve the minimum list of activities to keep in the graph, according to the percentage
        min_set_activities_to_keep = set(
            x[0] for x in activities_count_sorted_list[:math.ceil((len(activities_count) - 1) * percentage) + 1])
        # retrieve the activities that can be possibly discarded, according to the percentage
        activities_to_possibly_discard = list(
            x[0] for x in activities_count_sorted_list[math.ceil((len(activities_count) - 1) * percentage) + 1:])
        activities_to_possibly_discard.reverse()
        # build a graph structure that helps in deciding whether the activities can be discarded safely
        graph, start_node, end_node = generate_nx_graph_from_dfg(dfg, start_activities, end_activities,
                                                                 activities_count)
        for act in activities_to_possibly_discard:
            new_graph = nx_utils.DiGraph(graph)
            # try to remove the node
            new_graph.remove_node(act)
            # check whether all the activities to keep can be reached from the start and can reach the end
            reachable_from_start = set(nx_utils.descendants(new_graph, start_node))
            reachable_to_end = set(nx_utils.ancestors(new_graph, end_node))
            if min_set_activities_to_keep.issubset(reachable_from_start) and min_set_activities_to_keep.issubset(
                    reachable_to_end):
                # if that is the case, try to elaborate the new DFG (without the activity)
                new_dfg = {x: y for x, y in dfg.items() if x[0] != act and x[1] != act}
                # if that is still not empty ...
                if new_dfg:
                    # ... then the activity can be safely removed
                    dfg = new_dfg
                    del activities_count[act]
                    if act in start_activities:
                        del start_activities[act]
                    if act in end_activities:
                        del end_activities[act]
                    graph = new_graph

        # at the end of the previous step, some nodes may be remaining that are not reachable from the start
        # or cannot reach the end. obviously the previous steps ensured that at least the activities in min_set_activities_to_keep
        # are connected
        reachable_from_start = set(nx_utils.descendants(graph, start_node))
        reachable_to_end = set(nx_utils.ancestors(graph, end_node))
        reachable_start_end = reachable_from_start.intersection(reachable_to_end)
        activities_set = set(activities_count.keys())
        non_reachable_activities = activities_set.difference(reachable_start_end)

        # remove these non reachable activities
        for act in non_reachable_activities:
            dfg = {x: y for x, y in dfg.items() if x[0] != act and x[1] != act}
            del activities_count[act]
            if act in start_activities:
                del start_activities[act]
            if act in end_activities:
                del end_activities[act]

    return dfg, start_activities, end_activities, activities_count


def __filter_specified_paths(dfg, start_activities, end_activities, activities_count, graph, start_node, end_node,
                             discardable_edges, activities_not_to_discard):
    for edge in discardable_edges:
        if len(dfg) > 1:
            new_graph = nx_utils.DiGraph(graph)
            # try to remove the edge
            new_graph.remove_edge(edge[0], edge[1])

            # check whether all the activities to keep can be reached from the start and can reach the end
            reachable_from_start = set(nx_utils.descendants(new_graph, start_node))
            reachable_to_end = set(nx_utils.ancestors(new_graph, end_node))

            if activities_not_to_discard.issubset(reachable_from_start) and activities_not_to_discard.issubset(
                    reachable_to_end):
                # remove the edge
                graph = new_graph
                if edge in dfg:
                    # if the edge connects two activities simply remove that
                    del dfg[edge]
                elif edge[0] == start_node:
                    del start_activities[edge[1]]
                elif edge[1] == end_node:
                    del end_activities[edge[0]]

    # at the end of the previous step, some nodes may be remaining that are not reachable from the start
    # or cannot reach the end. obviously the previous steps ensured that at least the activities in min_set_activities_to_keep
    # are connected
    reachable_from_start = set(nx_utils.descendants(graph, start_node))
    reachable_to_end = set(nx_utils.ancestors(graph, end_node))
    reachable_start_end = reachable_from_start.intersection(reachable_to_end)
    activities_set = set(activities_count.keys())
    non_reachable_activities = activities_set.difference(reachable_start_end)

    # remove these non reachable activities
    for act in non_reachable_activities:
        dfg = {x: y for x, y in dfg.items() if x[0] != act and x[1] != act}
        del activities_count[act]
        if act in start_activities:
            del start_activities[act]
        if act in end_activities:
            del end_activities[act]

    # make sure that the DFG contains only edges between these activities
    dfg = {x: y for x, y in dfg.items() if x[0] in activities_count and x[1] in activities_count}

    return dfg, start_activities, end_activities, activities_count


def filter_dfg_on_paths_percentage(dfg0, start_activities0, end_activities0, activities_count0, percentage,
                                   keep_all_activities=False):
    """
    Filters a DFG (complete, and so connected) on the specified percentage of paths
    (but ensuring that every node is still reachable from the start and to the end)

    Parameters
    ----------------
    dfg0
        (Complete, and so connected) DFG
    start_activities0
        Start activities
    end_activities0
        End activities
    activities_count0
        Activities of the DFG along with their count
    percentage
        Percentage of paths
    keep_all_activities
        Decides if all the activities (also the ones connected by the low occurrences edges) should be kept,
        or only the ones appearing in the edges with more occurrences (default).

    Returns
    ----------------
    dfg
        (Filtered) DFG
    start_activities
        (Filtered) start activities
    end_activities
        (Filtered) end activities
    activities_count
        (Filtered) activities of the DFG along with their count
    """

    # since the dictionaries/sets are modified, a deepcopy is the best option to ensure data integrity
    dfg = deepcopy(dfg0)
    start_activities = deepcopy(start_activities0)
    end_activities = deepcopy(end_activities0)
    activities_count = deepcopy(activities_count0)

    if len(activities_count) > 1 and len(dfg) > 1:
        # build a graph structure that helps in deciding whether the paths can be discarded safely
        graph, start_node, end_node = generate_nx_graph_from_dfg(dfg, start_activities, end_activities,
                                                                 activities_count)
        all_edges = [(x, y) for x, y in dfg.items()] + [((start_node, x), start_activities[x]) for x in
                                                        start_activities] + [((x, end_node), end_activities[x]) for x in
                                                                             end_activities]
        all_edges = sorted(all_edges, key=lambda x: (x[1], x[0]), reverse=True)
        # calculate a set of edges that could be discarded and not
        non_discardable_edges = list(
            x[0] for x in all_edges[:math.ceil((len(all_edges) - 1) * percentage) + 1])
        discardable_edges = list(x[0] for x in all_edges[math.ceil((len(all_edges) - 1) * percentage) + 1:])
        discardable_edges.reverse()

        # according to the parameter's value, keep the activities that appears in the edges that should not be
        # discarded (default), OR keep all the activities, trying to remove edges but ensure connectiveness of
        # everything
        if keep_all_activities:
            activities_not_to_discard = set(x[0] for x in dfg).union(set(x[1] for x in dfg)).union(
                set(start_activities)).union(set(end_activities)).union(set(activities_count))
        else:
            activities_not_to_discard = set(x[0] for x in non_discardable_edges if not x[0] == start_node).union(
                set(x[1] for x in non_discardable_edges if not x[1] == end_node))

        dfg, start_activities, end_activities, activities_count = __filter_specified_paths(dfg, start_activities,
                                                                                           end_activities,
                                                                                           activities_count, graph,
                                                                                           start_node, end_node,
                                                                                           discardable_edges,
                                                                                           activities_not_to_discard)

    return dfg, start_activities, end_activities, activities_count


def filter_dfg_keep_connected(dfg0, start_activities0, end_activities0, activities_count0, threshold,
                              keep_all_activities=False):
    """
    Filters a DFG (complete, and so connected) on the specified dependency threshold (Heuristics Miner dependency)
    (but ensuring that every node is still reachable from the start and to the end)

    Parameters
    ----------------
    dfg0
        (Complete, and so connected) DFG
    start_activities0
        Start activities
    end_activities0
        End activities
    activities_count0
        Activities of the DFG along with their count
    threshold
        Dependency threshold as in the Heuristics Miner
    keep_all_activities
        Decides if all the activities should be kept,
        or only the ones appearing in the edges with higher threshold (default).

    Returns
    ----------------
    dfg
        (Filtered) DFG
    start_activities
        (Filtered) start activities
    end_activities
        (Filtered) end activities
    activities_count
        (Filtered) activities of the DFG along with their count
    """

    # since the dictionaries/sets are modified, a deepcopy is the best option to ensure data integrity
    dfg = deepcopy(dfg0)
    start_activities = deepcopy(start_activities0)
    end_activities = deepcopy(end_activities0)
    activities_count = deepcopy(activities_count0)

    if len(activities_count) > 1 and len(dfg) > 1:
        # build a graph structure that helps in deciding whether the paths can be discarded safely
        graph, start_node, end_node = generate_nx_graph_from_dfg(dfg, start_activities, end_activities,
                                                                 activities_count)

        dependency = {}
        for el in dfg:
            elinv = (el[1], el[0])
            if elinv in dfg:
                dep = (dfg[el] - dfg[elinv]) / (dfg[el] + dfg[elinv] + 1)
            else:
                dep = dfg[el] / (dfg[el] + 1)
            dependency[el] = dep

        all_edges = [(x, y) for x, y in dependency.items()] + [((start_node, x), 1.0) for x in
                                                        start_activities] + [((x, end_node), 1.0) for x in
                                                                             end_activities]
        all_edges = sorted(all_edges, key=lambda x: (x[1], x[0]), reverse=True)
        # calculate a set of edges that could be discarded and not
        non_discardable_edges = list(x[0] for x in all_edges if x[1] >= threshold)
        discardable_edges = list(x[0] for x in all_edges if x[1] < threshold)
        discardable_edges.reverse()

        # according to the parameter's value, keep the activities that appears in the edges that should not be
        # discarded (default), OR keep all the activities, trying to remove edges but ensure connectiveness of
        # everything
        if keep_all_activities:
            activities_not_to_discard = set(x[0] for x in dfg).union(set(x[1] for x in dfg)).union(
                set(start_activities)).union(set(end_activities)).union(set(activities_count))
        else:
            activities_not_to_discard = set(x[0] for x in non_discardable_edges if not x[0] == start_node).union(
                set(x[1] for x in non_discardable_edges if not x[1] == end_node))

        dfg, start_activities, end_activities, activities_count = __filter_specified_paths(dfg, start_activities,
                                                                                           end_activities,
                                                                                           activities_count, graph,
                                                                                           start_node, end_node,
                                                                                           discardable_edges,
                                                                                           activities_not_to_discard)

    return dfg, start_activities, end_activities, activities_count


def filter_dfg_to_activity(dfg0, start_activities0, end_activities0, activities_count0, target_activity,
                           parameters=None):
    """
    Filters the DFG, making "target_activity" the only possible end activity of the graph

    Parameters
    ---------------
    dfg0
        Directly-follows graph
    start_activities0
        Start activities
    end_activities0
        End activities
    activities_count0
        Activities count
    target_activity
        Target activity (only possible end activity after the filtering)
    parameters
        Parameters

    Returns
    ---------------
    dfg
        Filtered DFG
    start_activities
        Filtered start activities
    end_activities
        Filtered end activities
    activities_count
        Filtered activities count
    """
    if parameters is None:
        parameters = {}

    # since the dictionaries/sets are modified, a deepcopy is the best option to ensure data integrity
    dfg = deepcopy(dfg0)
    start_activities = deepcopy(start_activities0)
    activities_count = deepcopy(activities_count0)

    dfg = {x: y for x, y in dfg.items() if x[0] != target_activity}
    end_activities = {target_activity: activities_count[target_activity]}

    changed = True
    while changed:
        changed = False
        predecessors = dfg_utils.get_predecessors(dfg, activities_count)
        successors = dfg_utils.get_successors(dfg, activities_count)

        successors_from_sa = set()
        for act in start_activities:
            successors_from_sa = successors_from_sa.union(successors[act])
            successors_from_sa.add(act)

        reachable_nodes = successors_from_sa.intersection(predecessors[target_activity]).union({target_activity})
        if reachable_nodes != set(activities_count.keys()):
            changed = True
            activities_count = {x: y for x, y in activities_count.items() if x in reachable_nodes}
            start_activities = {x: y for x, y in start_activities.items() if x in reachable_nodes}
            dfg = {x: y for x, y in dfg.items() if x[0] in reachable_nodes and x[1] in reachable_nodes}

    return dfg, start_activities, end_activities, activities_count


def filter_dfg_from_activity(dfg0, start_activities0, end_activities0, activities_count0, source_activity,
                             parameters=None):
    """
    Filters the DFG, making "source_activity" the only possible source activity of the graph

    Parameters
    ---------------
    dfg0
        Directly-follows graph
    start_activities0
        Start activities
    end_activities0
        End activities
    activities_count0
        Activities count
    source_activity
        Source activity (only possible start activity after the filtering)
    parameters
        Parameters

    Returns
    ---------------
    dfg
        Filtered DFG
    start_activities
        Filtered start activities
    end_activities
        Filtered end activities
    activities_count
        Filtered activities count
    """
    if parameters is None:
        parameters = {}

    # since the dictionaries/sets are modified, a deepcopy is the best option to ensure data integrity
    dfg = deepcopy(dfg0)
    end_activities = deepcopy(end_activities0)
    activities_count = deepcopy(activities_count0)

    dfg = {x: y for x, y in dfg.items() if x[1] != source_activity}
    start_activities = {source_activity: activities_count[source_activity]}

    changed = True
    while changed:
        changed = False
        predecessors = dfg_utils.get_predecessors(dfg, activities_count)
        successors = dfg_utils.get_successors(dfg, activities_count)

        predecessors_from_ea = set()
        for ea in end_activities:
            predecessors_from_ea = predecessors_from_ea.union(predecessors[ea])
            predecessors_from_ea.add(ea)

        reachable_nodes = predecessors_from_ea.intersection(successors[source_activity]).union({source_activity})
        if reachable_nodes != set(activities_count.keys()):
            changed = True
            activities_count = {x: y for x, y in activities_count.items() if x in reachable_nodes}
            end_activities = {x: y for x, y in end_activities.items() if x in reachable_nodes}
            dfg = {x: y for x, y in dfg.items() if x[0] in reachable_nodes and x[1] in reachable_nodes}

    return dfg, start_activities, end_activities, activities_count


def filter_dfg_contain_activity(dfg0, start_activities0, end_activities0, activities_count0, activity, parameters=None):
    """
    Filters the DFG keeping only nodes that can reach / are reachable from activity

    Parameters
    ---------------
    dfg0
        Directly-follows graph
    start_activities0
        Start activities
    end_activities0
        End activities
    activities_count0
        Activities count
    activity
        Activity that should be reachable / should reach all the nodes of the filtered graph
    parameters
        Parameters

    Returns
    ---------------
    dfg
        Filtered DFG
    start_activities
        Filtered start activities
    end_activities
        Filtered end activities
    activities_count
        Filtered activities count
    """
    if parameters is None:
        parameters = {}

    # since the dictionaries/sets are modified, a deepcopy is the best option to ensure data integrity
    dfg = deepcopy(dfg0)
    start_activities = deepcopy(start_activities0)
    end_activities = deepcopy(end_activities0)
    activities_count = deepcopy(activities_count0)

    changed = True
    while changed:
        changed = False
        predecessors = dfg_utils.get_predecessors(dfg, activities_count)
        successors = dfg_utils.get_successors(dfg, activities_count)

        predecessors_act = predecessors[activity].union({activity})
        successors_act = successors[activity].union({activity})

        start_activities1 = {x: y for x, y in start_activities.items() if x in predecessors_act}
        end_activities1 = {x: y for x, y in end_activities.items() if x in successors_act}

        if start_activities != start_activities1 or end_activities != end_activities1:
            changed = True

        start_activities = start_activities1
        end_activities = end_activities1

        reachable_nodes = predecessors_act.union(successors_act)
        if reachable_nodes != set(activities_count.keys()):
            changed = True
            activities_count = {x: y for x, y in activities_count.items() if x in reachable_nodes}
            dfg = {x: y for x, y in dfg.items() if x[0] in reachable_nodes and x[1] in reachable_nodes}

    return dfg, start_activities, end_activities, activities_count


def clean_dfg_based_on_noise_thresh(dfg, activities, noise_threshold, parameters=None):
    """
    Clean Directly-Follows graph based on noise threshold

    Parameters
    ----------
    dfg
        Directly-Follows graph
    activities
        Activities in the DFG graph
    noise_threshold
        Noise threshold

    Returns
    ----------
    newDfg
        Cleaned dfg based on noise threshold
    """
    if parameters is None:
        parameters = {}

    most_common_paths = parameters[
        constants.PARAM_MOST_COMMON_PATHS] if constants.PARAM_MOST_COMMON_PATHS in parameters else None
    if most_common_paths is None:
        most_common_paths = []

    new_dfg = None
    activ_max_count = {}
    for act in activities:
        activ_max_count[act] = dfg_utils.get_max_activity_count(dfg, act)

    for el in dfg:
        if type(el[0]) is str:
            if new_dfg is None:
                new_dfg = {}
            act1 = el[0]
            act2 = el[1]
            val = dfg[el]
        else:
            if new_dfg is None:
                new_dfg = []
            act1 = el[0][0]
            act2 = el[0][1]
            val = el[1]

        if not el in most_common_paths and val < min(activ_max_count[act1] * noise_threshold,
                                                     activ_max_count[act2] * noise_threshold):
            pass
        else:
            if type(el[0]) is str:
                new_dfg[el] = dfg[el]
                pass
            else:
                new_dfg.append(el)
                pass

    if new_dfg is None:
        return dfg

    return new_dfg

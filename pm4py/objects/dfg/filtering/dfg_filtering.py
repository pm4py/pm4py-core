import math
import uuid

from pm4py.objects.dfg.utils.dfg_utils import get_max_activity_count
from pm4py.util import constants
from copy import deepcopy

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
    import networkx as nx
    start_node = str(uuid.uuid4())
    end_node = str(uuid.uuid4())
    G = nx.DiGraph()
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
    import networkx as nx

    # since the dictionaries/sets are modified, a deepcopy is the best option to ensure data integrity
    dfg = deepcopy(dfg0)
    start_activities = deepcopy(start_activities0)
    end_activities = deepcopy(end_activities0)
    activities_count = deepcopy(activities_count0)

    if len(activities_count) > 1 and len(dfg) > 1:
        activities_count_sorted_list = sorted([(x, y) for x, y in activities_count.items()], key=lambda x: x[1],
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
            new_graph = nx.DiGraph(graph)
            # try to remove the node
            new_graph.remove_node(act)
            # check whether all the activities to keep can be reached from the start and can reach the end
            reachable_from_start = set(nx.descendants(new_graph, start_node))
            reachable_to_end = set(nx.ancestors(new_graph, end_node))
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
        reachable_from_start = set(nx.descendants(graph, start_node))
        reachable_to_end = set(nx.ancestors(graph, end_node))
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
    import networkx as nx

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
        all_edges = sorted(all_edges, key=lambda x: x[1], reverse=True)
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
        for edge in discardable_edges:
            if len(dfg) > 1:
                new_graph = nx.DiGraph(graph)
                # try to remove the edge
                new_graph.remove_edge(edge[0], edge[1])

                # check whether all the activities to keep can be reached from the start and can reach the end
                reachable_from_start = set(nx.descendants(new_graph, start_node))
                reachable_to_end = set(nx.ancestors(new_graph, end_node))

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
        reachable_from_start = set(nx.descendants(graph, start_node))
        reachable_to_end = set(nx.ancestors(graph, end_node))
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
        activ_max_count[act] = get_max_activity_count(dfg, act)

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

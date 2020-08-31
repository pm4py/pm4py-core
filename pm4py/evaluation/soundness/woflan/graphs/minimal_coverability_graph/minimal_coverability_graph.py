"""
This module is based on:
The minimal coverability graph for Petri nets
from Alain Finkel
"""
import numpy as np
import networkx as nx
from pm4py.evaluation.soundness.woflan.graphs import utility as helper
from copy import copy


def minimal_coverability_tree(net, initial_marking, original_net=None):
    """
    This method computes the minimal coverability tree. It is part of a method to obtain a minial coverability graph
    :param net: Petri Net
    :param initial_marking: Initial Marking of the Petri Net
    :param original_net: Petri Net without short-circuited transition
    :return: Minimal coverability tree
    """

    def check_if_marking_already_in_processed_nodes(n, processed_nodes):
        for node in processed_nodes:
            if np.array_equal(G.nodes[node]['marking'], G.nodes[n]['marking']):
                return True
        return False

    def is_m_smaller_than_other(m, processed_nodes):
        for node in processed_nodes:
            if all(np.less_equal(m, G.nodes[node]['marking'])):
                return True
        return False

    def is_m_greater_than_other(m, processed_nodes):
        for node in processed_nodes:
            if all(np.greater_equal(m, G.nodes[node]['marking'])):
                return True
        return False

    def get_first_smaller_marking_on_path(n, m2):
        path = nx.shortest_path(G, source=0, target=n)
        for node in path:
            if all(np.less_equal(G.nodes[node]['marking'], m2)):
                return node
        return None

    def remove_subtree(tree, n):
        bfs_tree = nx.bfs_tree(tree, n)
        for edge in bfs_tree.edges:
            tree.remove_edge(edge[0], edge[1])
        for node in bfs_tree.nodes:
            if node != n:
                tree.remove_node(node)
        return tree

    G = nx.MultiDiGraph()

    incidence_matrix = helper.compute_incidence_matrix(net)
    firing_dict = helper.split_incidence_matrix(incidence_matrix, net)
    req_dict = helper.compute_firing_requirement(net)

    initial_mark = helper.convert_marking(net, initial_marking, original_net)
    j = 0
    unprocessed_nodes = set()
    G.add_node(j, marking=initial_mark)
    unprocessed_nodes.add(j)
    j += 1

    processed_nodes = set()

    while len(unprocessed_nodes) > 0:
        n = unprocessed_nodes.pop()
        if check_if_marking_already_in_processed_nodes(n, processed_nodes):
            processed_nodes.add(n)
        elif is_m_smaller_than_other(G.nodes[n]['marking'], processed_nodes):
            G.remove_edge(next(G.predecessors(n)), n)
            G.remove_node(n)
        elif is_m_greater_than_other(G.nodes[n]['marking'], processed_nodes):
            m2 = G.nodes[n]['marking'].copy()
            ancestor_bool = False
            for ancestor in nx.ancestors(G, n):
                if is_m_greater_than_other(G.nodes[n]['marking'], [ancestor]):
                    i = 0
                    while i < len(G.nodes[n]['marking']):
                        if G.nodes[ancestor]['marking'][i] < G.nodes[n]['marking'][i]:
                            m2[i] = np.inf
                        i += 1
            n1 = None
            for ancestor in nx.ancestors(G, n):
                if all(np.less_equal(G.nodes[ancestor]['marking'], m2)):
                    n1 = get_first_smaller_marking_on_path(n, m2)
                    break
            if n1 != None:
                ancestor_bool = True
                G.nodes[n1]['marking'] = m2.copy()
                subtree = nx.bfs_tree(G, n1)
                for node in subtree:
                    if node in processed_nodes:
                        processed_nodes.remove(node)
                    if node in unprocessed_nodes:
                        unprocessed_nodes.remove(node)
                G = remove_subtree(G, n1)
                unprocessed_nodes.add(n1)
            processed_nodes_copy = copy(processed_nodes)
            for node in processed_nodes_copy:
                if node in G.nodes:
                    if all(np.less_equal(G.nodes[node]['marking'], m2)):
                        subtree = nx.bfs_tree(G, node)
                        for node in subtree:
                            if node in processed_nodes:
                                processed_nodes.remove(node)
                            if node in unprocessed_nodes:
                                unprocessed_nodes.remove(node)
                        remove_subtree(G, node)
                        G.remove_node(node)
            if not ancestor_bool:
                unprocessed_nodes.add(n)
        else:
            for el in helper.enabled_markings(firing_dict, req_dict, G.nodes[n]['marking']):
                G.add_node(j, marking=el[0])
                G.add_edge(n, j, transition=el[1])
                unprocessed_nodes.add(j)
                j += 1
            processed_nodes.add(n)
    return (G, firing_dict, req_dict)


def apply(net, initial_marking, original_net=None):
    """
    Apply method from the "outside".
    :param net: Petri Net object
    :param initial_marking: Initial marking of the Petri Net object
    :param original_net: Petri Net object without short-circuited transition. For better usability, initial set to None
    :return: MultiDiGraph networkx object
    """

    def detect_same_labelled_nodes(G):
        same_labels = {}
        for node in G.nodes:
            if np.array2string(G.nodes[node]['marking']) not in same_labels:
                same_labels[np.array2string(G.nodes[node]['marking'])] = [node]
            else:
                same_labels[np.array2string(G.nodes[node]['marking'])].append(node)
        return same_labels

    def merge_nodes_of_same_label(G, same_labels):
        for marking in same_labels:
            if len(same_labels[marking]) > 1:
                origin = same_labels[marking][0]
                i = 1
                while i < len(same_labels[marking]):
                    G = nx.contracted_nodes(G, origin, same_labels[marking][i])
                    i += 1
        return G

    mct, firing_dict, req_dict = minimal_coverability_tree(net, initial_marking, original_net)
    mcg = merge_nodes_of_same_label(mct, detect_same_labelled_nodes(mct))

    to_remove_edges = []
    for edge in mcg.edges:
        reachable_markings = helper.enabled_markings(firing_dict, req_dict, mcg.nodes[edge[0]]['marking'])
        not_reachable = True
        for el in reachable_markings:
            if np.array_equal(el[0], mcg.nodes[edge[1]]['marking']):
                not_reachable = False
                break
        if not_reachable:
            to_remove_edges.append(edge)
    for edge in to_remove_edges:
        mcg.remove_edge(edge[0], edge[1])
    return mcg

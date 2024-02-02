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
"""
This module is based on:
The minimal coverability graph for Petri nets
from Alain Finkel
"""
import numpy as np
from pm4py.util import nx_utils
from pm4py.algo.analysis.woflan.graphs import utility as helper
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
        path = nx_utils.shortest_path(G, source=0, target=n)
        for node in path:
            if all(np.less_equal(G.nodes[node]['marking'], m2)):
                return node
        return None

    def remove_subtree(tree, n):
        bfs_tree = nx_utils.bfs_tree(tree, n)
        for edge in bfs_tree.edges:
            tree.remove_edge(edge[0], edge[1])
        for node in bfs_tree.nodes:
            if node != n:
                tree.remove_node(node)
        return tree

    G = nx_utils.MultiDiGraph()

    incidence_matrix = helper.compute_incidence_matrix(net)
    firing_dict = helper.split_incidence_matrix(incidence_matrix, net)
    req_dict = helper.compute_firing_requirement(net)

    initial_mark = helper.convert_marking(net, initial_marking, original_net)
    j = 0
    unprocessed_nodes = list()
    G.add_node(j, marking=initial_mark)
    unprocessed_nodes.append(j)
    j += 1

    processed_nodes = set()

    while len(unprocessed_nodes) > 0:
        n = unprocessed_nodes.pop()
        if check_if_marking_already_in_processed_nodes(n, processed_nodes):
            processed_nodes.add(n)
        elif is_m_smaller_than_other(G.nodes[n]['marking'], processed_nodes):
            predecessors = sorted(list(G.predecessors(n)))
            G.remove_edge(predecessors[0], n)
            G.remove_node(n)
        elif is_m_greater_than_other(G.nodes[n]['marking'], processed_nodes):
            m2 = G.nodes[n]['marking'].copy()
            ancestor_bool = False
            ancestors = sorted(list(nx_utils.ancestors(G, n)))
            for ancestor in ancestors:
                if is_m_greater_than_other(G.nodes[n]['marking'], [ancestor]):
                    i = 0
                    while i < len(G.nodes[n]['marking']):
                        if G.nodes[ancestor]['marking'][i] < G.nodes[n]['marking'][i]:
                            m2[i] = np.inf
                        i += 1
            n1 = None
            for ancestor in ancestors:
                if all(np.less_equal(G.nodes[ancestor]['marking'], m2)):
                    n1 = get_first_smaller_marking_on_path(n, m2)
                    break
            if n1 != None:
                ancestor_bool = True
                G.nodes[n1]['marking'] = m2.copy()
                subtree = sorted(list(nx_utils.bfs_tree(G, n1)))
                for node in subtree:
                    if node in processed_nodes:
                        processed_nodes.remove(node)
                    if node in unprocessed_nodes:
                        del unprocessed_nodes[unprocessed_nodes.index(node)]
                G = remove_subtree(G, n1)
                if not n1 in unprocessed_nodes:
                    unprocessed_nodes.append(n1)
            processed_nodes_copy = copy(processed_nodes)
            for node in processed_nodes_copy:
                if node in G.nodes:
                    if all(np.less_equal(G.nodes[node]['marking'], m2)):
                        subtree = nx_utils.bfs_tree(G, node)
                        for node in subtree:
                            if node in processed_nodes:
                                processed_nodes.remove(node)
                            if node in unprocessed_nodes:
                                del unprocessed_nodes[unprocessed_nodes.index(node)]
                        remove_subtree(G, node)
                        G.remove_node(node)
            if not ancestor_bool:
                if n not in unprocessed_nodes:
                    unprocessed_nodes.append(n)
        else:
            enabled_markings = helper.enabled_markings(firing_dict, req_dict, G.nodes[n]['marking'])
            for el in enabled_markings:
                G.add_node(j, marking=el[0])
                G.add_edge(n, j, transition=el[1])
                if j not in unprocessed_nodes:
                    unprocessed_nodes.append(j)
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
                    G = nx_utils.contracted_nodes(G, origin, same_labels[marking][i])
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

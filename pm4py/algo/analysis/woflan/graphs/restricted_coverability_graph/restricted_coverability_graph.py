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
import numpy as np
from pm4py.algo.analysis.woflan.graphs import utility as helper
from pm4py.util import nx_utils


def construct_tree(net, initial_marking):
    """
    Construct a restricted coverability marking.
    For more information, see the thesis "Verification of WF-nets", 4.3.
    :param net:
    :param initial_marking:
    :return:
    """
    initial_marking = helper.convert_marking(net, initial_marking)
    firing_dict = helper.split_incidence_matrix(helper.compute_incidence_matrix(net), net)
    req_dict = helper.compute_firing_requirement(net)
    look_up_indices = {}
    j = 0
    coverability_graph = nx_utils.DiGraph()
    coverability_graph.add_node(j, marking=initial_marking)
    look_up_indices[np.array2string(initial_marking)] = j

    j += 1
    new_arc = True
    while new_arc:
        new_arc = False
        nodes = list(coverability_graph.nodes).copy()
        while len(nodes) > 0:
            m = nodes.pop()
            if not np.inf in coverability_graph.nodes[m]['marking']:
                possible_markings = helper.enabled_markings(firing_dict, req_dict,
                                                            coverability_graph.nodes[m]['marking'])
                m2 = None
                if len(possible_markings) > 0:
                    for marking in possible_markings:
                        # check for m1 + since we want to construct a tree, we do not want that a marking is already in a graph since it is going to have an arc
                        if np.array2string(marking[0]) not in look_up_indices:
                            if check_if_transition_unique(m, coverability_graph, marking[1]):
                                m2 = marking
                                new_arc = True
                                break
                if new_arc:
                    break
        if new_arc:
            lplaces = sorted(list(net.places), key=lambda x: x.name)
            m3 = np.zeros(len(lplaces))
            for place in lplaces:
                if check_for_smaller_marking(m2, coverability_graph, lplaces.index(place), m, look_up_indices):
                    m3[lplaces.index(place)] = np.inf
                else:
                    m3[lplaces.index(place)] = m2[0][lplaces.index(place)]
            coverability_graph.add_node(j, marking=m3)
            coverability_graph.add_edge(m, j, transition=m2[1])
            look_up_indices[np.array2string(m3)] = j
            j += 1
    return coverability_graph


def check_if_transition_unique(marking, graph, transition):
    for edge in graph.out_edges(marking):
        if graph[edge[0]][edge[1]]['transition'] == transition:
            return False
    return True


def check_for_smaller_marking(marking, coverability_graph, index, current_node, look_up_indices):
    for node in coverability_graph.nodes:
        if all(np.less_equal(coverability_graph.nodes[node]['marking'], marking[0])):
            if coverability_graph.nodes[node]['marking'][index] < marking[0][index]:
                if nx_utils.has_path(coverability_graph,
                               look_up_indices[np.array2string(coverability_graph.nodes[node]['marking'])],
                               current_node):
                    return True
    return False

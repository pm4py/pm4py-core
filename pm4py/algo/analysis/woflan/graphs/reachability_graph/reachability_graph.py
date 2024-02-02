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
from pm4py.util import nx_utils
import numpy as np
from pm4py.algo.analysis.woflan.graphs import utility as helper


def apply(net, initial_marking, original_net=None):
    """
    Method that computes a reachability graph as networkx object
    :param net: Petri Net
    :param initial_marking: Initial Marking of the Petri Net
    :param original_net: Petri Net without short-circuited transition
    :return: Networkx Graph that represents the reachability graph of the Petri Net
    """
    initial_marking = helper.convert_marking(net, initial_marking, original_net)
    firing_dict = helper.split_incidence_matrix(helper.compute_incidence_matrix(net), net)
    req_dict = helper.compute_firing_requirement(net)
    look_up_indices = {}
    j = 0
    reachability_graph = nx_utils.MultiDiGraph()
    reachability_graph.add_node(j, marking=initial_marking)

    working_set = set()
    working_set.add(j)

    look_up_indices[np.array2string(initial_marking)] = j

    j += 1
    while len(working_set) > 0:
        m = working_set.pop()
        possible_markings = helper.enabled_markings(firing_dict, req_dict, reachability_graph.nodes[m]['marking'])
        for marking in possible_markings:
            if np.array2string(marking[0]) not in look_up_indices:
                look_up_indices[np.array2string(marking[0])] = j
                reachability_graph.add_node(j, marking=marking[0])
                working_set.add(j)
                reachability_graph.add_edge(m, j, transition=marking[1])
                j += 1
            else:
                reachability_graph.add_edge(m, look_up_indices[np.array2string(marking[0])], transition=marking[1])
    return reachability_graph

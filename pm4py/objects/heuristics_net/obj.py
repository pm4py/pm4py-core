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
from copy import deepcopy

from pm4py.objects.dfg.utils import dfg_utils

DEFAULT_NET_NAME = ""


class HeuristicsNet:
    def __init__(self, frequency_dfg, activities=None, start_activities=None, end_activities=None,
                 activities_occurrences=None,
                 default_edges_color="#000000", performance_dfg=None, dfg_window_2=None, freq_triples=None,
                 net_name=DEFAULT_NET_NAME):
        """
        Initialize an Hueristics Net

        The implementation is based on the original paper on Heuristics Miner, namely:

        Weijters, A. J. M. M., Wil MP van Der Aalst, and AK Alves De Medeiros.
        "Process mining with the heuristics miner-algorithm."
        Technische Universiteit Eindhoven, Tech. Rep. WP 166 (2006): 1-34.

        and it manages to calculate the dependency matrix, the loops of length one and two, and
        the AND measure

        Parameters
        -------------
        frequency_dfg
            Directly-Follows graph (frequency)
        activities
            Activities
        start_activities
            Start activities
        end_activities
            End activities
        activities_occurrences
            Activities occurrences
        default_edges_color
            (If provided) Default edges color
        performance_dfg
            Performance DFG
        dfg_window_2
            DFG window 2
        freq_triples
            Frequency triples
        net_name
            (If provided) name of the heuristics net
        """
        self.net_name = [net_name]

        self.nodes = {}
        self.dependency_matrix = {}
        self.dfg_matrix = {}

        self.dfg = frequency_dfg
        self.performance_dfg = performance_dfg
        self.node_type = "frequency" if self.performance_dfg is None else "performance"

        self.activities = activities
        if self.activities is None:
            self.activities = dfg_utils.get_activities_from_dfg(frequency_dfg)
        if start_activities is None:
            self.start_activities = [dfg_utils.infer_start_activities(frequency_dfg)]
        else:
            self.start_activities = [start_activities]
        if end_activities is None:
            self.end_activities = [dfg_utils.infer_end_activities(frequency_dfg)]
        else:
            self.end_activities = [end_activities]
        self.activities_occurrences = activities_occurrences
        if self.activities_occurrences is None:
            self.activities_occurrences = {}
            for act in self.activities:
                self.activities_occurrences[act] = dfg_utils.sum_activities_count(frequency_dfg, [act])
        self.default_edges_color = [default_edges_color]
        self.dfg_window_2 = dfg_window_2
        self.dfg_window_2_matrix = {}
        self.freq_triples = freq_triples
        self.freq_triples_matrix = {}
        self.concurrent_activities = {}
        self.sojourn_times = {}

    def __add__(self, other_net):
        copied_self = deepcopy(self)
        for node_name in copied_self.nodes:
            if node_name in other_net.nodes:
                node1 = copied_self.nodes[node_name]
                node2 = other_net.nodes[node_name]
                n1n = {x.node_name: x for x in node1.output_connections}
                n2n = {x.node_name: x for x in node2.output_connections}
                for out_node1 in node1.output_connections:
                    if out_node1.node_name in n2n:
                        node1.output_connections[out_node1] = node1.output_connections[out_node1] + \
                                                              node2.output_connections[n2n[out_node1.node_name]]
                for out_node2 in node2.output_connections:
                    if out_node2.node_name not in n1n:
                        if out_node2.node_name in copied_self.nodes:
                            nn = copied_self.nodes[out_node2.node_name]
                            node1.output_connections[nn] = node2.output_connections[out_node2]
                        else:
                            node1.output_connections[out_node2] = node2.output_connections[out_node2]
        diffext = [other_net.nodes[node] for node in other_net.nodes if node not in copied_self.nodes]
        for node in diffext:
            copied_self.nodes[node.node_name] = node
        copied_self.start_activities = copied_self.start_activities + other_net.start_activities
        copied_self.end_activities = copied_self.end_activities + other_net.end_activities
        copied_self.default_edges_color = copied_self.default_edges_color + other_net.default_edges_color
        copied_self.net_name = copied_self.net_name + other_net.net_name

        return copied_self

    def __repr__(self):
        return str(self.nodes)

    def __str__(self):
        return str(self.nodes)

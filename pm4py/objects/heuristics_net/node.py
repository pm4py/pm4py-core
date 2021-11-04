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
from pm4py.objects.heuristics_net import defaults
from pm4py.objects.heuristics_net.edge import Edge


class Node:
    def __init__(self, heuristics_net, node_name, node_occ, is_start_node=False, is_end_node=False,
                 default_edges_color="#000000", node_type="frequency", net_name="", nodes_dictionary=None):
        """
        Constructor

        Parameters
        -------------
        heuristics_net
            Parent heuristics net
        node_name
            Name of the node (may be the activity)
        node_occ
            Occurrences of the node
        is_start_node
            Tells if the node is a start node
        is_end_node
            Tells if the node is a end node
        default_edges_color
            Default edges color
        node_type
            Type of the node (frequency/performance)
        net_name
            (If provided) name of the Heuristics Net
        """
        self.heuristics_net = heuristics_net
        self.node_name = node_name
        self.node_occ = node_occ
        self.is_start_activity = is_start_node
        self.is_end_activity = is_end_node
        self.input_connections = {}
        self.output_connections = {}
        self.and_measures_in = {}
        self.and_measures_out = {}
        self.loop_length_two = {}
        self.output_couples_and_measure = []
        self.default_edges_color = default_edges_color
        self.node_type = node_type
        self.net_name = net_name
        self.nodes_dictionary = nodes_dictionary
        self.fill_color = None
        self.font_color = None

    def add_output_connection(self, other_node, dependency_value, dfg_value, repr_color=None, repr_value=None):
        """
        Adds an output connection to another node

        Parameters
        -------------
        other_node
            Other node
        dependency_value
            Dependency value
        dfg_value
            DFG value
        repr_color
            Color associated to the edge
        repr_value
            Value associated to the edge (if None, dfg_value is used)
        """
        if repr_color is None:
            repr_color = self.default_edges_color
        if repr_value is None:
            repr_value = dfg_value
        edge = Edge(self, other_node, dependency_value, dfg_value, repr_value, repr_color=repr_color,
                    edge_type=self.node_type, net_name=self.net_name)
        if other_node not in self.output_connections:
            self.output_connections[other_node] = []
        self.output_connections[other_node].append(edge)

    def add_input_connection(self, other_node, dependency_value, dfg_value, repr_color=None, repr_value=None):
        """
        Adds an input connection to another node

        Parameters
        -------------
        other_node
            Other node
        dependency_value
            Dependency value
        dfg_value
            DFG value
        repr_color
            Color associated to the edge
        repr_value
            Value associated to the edge (if None, dfg_value is used)
        """
        if repr_color is None:
            repr_color = self.default_edges_color
        if repr_value is None:
            repr_value = dfg_value
        edge = Edge(self, other_node, dependency_value, dfg_value, repr_value, repr_color=repr_color,
                    edge_type=self.node_type, net_name=self.net_name)
        if other_node not in self.input_connections:
            self.input_connections[other_node] = []
        self.input_connections[other_node].append(edge)

    def calculate_and_measure_out(self, and_measure_thresh=defaults.AND_MEASURE_THRESH):
        """
        Calculate AND measure for output relations (as couples)

        Parameters
        -------------
        and_measure_thresh
            AND measure threshold
        """
        out_nodes = sorted(list(self.output_connections), key=lambda x: x.node_name)
        i = 0
        while i < len(out_nodes):
            n1 = out_nodes[i].node_name
            j = i + 1
            while j < len(out_nodes):
                n2 = out_nodes[j].node_name
                c1 = self.heuristics_net.dfg_matrix[n1][n2] if n1 in self.heuristics_net.dfg_matrix and n2 in \
                                                               self.heuristics_net.dfg_matrix[n1] else 0
                c2 = self.heuristics_net.dfg_matrix[n2][n1] if n2 in self.heuristics_net.dfg_matrix and n1 in \
                                                               self.heuristics_net.dfg_matrix[n2] else 0
                c3 = self.heuristics_net.dfg_matrix[self.node_name][n1] if self.node_name in self.heuristics_net.dfg_matrix and n1 in self.heuristics_net.dfg_matrix[self.node_name] else 0
                c4 = self.heuristics_net.dfg_matrix[self.node_name][n2] if self.node_name in self.heuristics_net.dfg_matrix and n2 in self.heuristics_net.dfg_matrix[self.node_name] else 0
                value = (c1 + c2) / (c3 + c4 + 1)
                if value >= and_measure_thresh:
                    if n1 not in self.and_measures_out:
                        self.and_measures_out[n1] = {}
                    self.and_measures_out[n1][n2] = value
                j = j + 1
            i = i + 1

    def calculate_and_measure_in(self, and_measure_thresh=defaults.AND_MEASURE_THRESH):
        """
        Calculate AND measure for input relations (as couples)

        Parameters
        --------------
        and_measure_thresh
            AND measure threshold
        """
        in_nodes = sorted(list(self.input_connections), key=lambda x: x.node_name)
        i = 0
        while i < len(in_nodes):
            n1 = in_nodes[i].node_name
            j = i + 1
            while j < len(in_nodes):
                n2 = in_nodes[j].node_name
                c1 = self.heuristics_net.dfg_matrix[n1][n2] if n1 in self.heuristics_net.dfg_matrix and n2 in \
                                                               self.heuristics_net.dfg_matrix[n1] else 0
                c2 = self.heuristics_net.dfg_matrix[n2][n1] if n2 in self.heuristics_net.dfg_matrix and n1 in \
                                                               self.heuristics_net.dfg_matrix[n2] else 0
                c3 = self.heuristics_net.dfg_matrix[n1][self.node_name] if n1 in self.heuristics_net.dfg_matrix and self.node_name in self.heuristics_net.dfg_matrix[n1] else 0
                c4 = self.heuristics_net.dfg_matrix[n2][self.node_name] if n2 in self.heuristics_net.dfg_matrix and self.node_name in self.heuristics_net.dfg_matrix[n2] else 0
                value = (c1 + c2) / (c3 + c4 + 1)
                if value >= and_measure_thresh:
                    if n1 not in self.and_measures_in:
                        self.and_measures_in[n1] = {}
                    self.and_measures_in[n1][n2] = value
                j = j + 1
            i = i + 1

    def calculate_loops_length_two(self, dfg_matrix, freq_triples_matrix,
                                   loops_length_two_thresh=defaults.DEFAULT_LOOP_LENGTH_TWO_THRESH):
        """
        Calculate loops of length two

        Parameters
        --------------
        dfg_matrix
            DFG matrix
        freq_triples_matrix
            Matrix of triples
        loops_length_two_thresh
            Loops length two threshold
        """
        if self.nodes_dictionary is not None and self.node_name in freq_triples_matrix:
            n1 = self.node_name
            for n2 in freq_triples_matrix[n1]:
                c1 = dfg_matrix[n1][n2] if n1 in dfg_matrix and n2 in dfg_matrix[n1] else 0
                v1 = freq_triples_matrix[n1][n2] if n1 in freq_triples_matrix and n2 in freq_triples_matrix[n1] else 0
                v2 = freq_triples_matrix[n2][n1] if n2 in freq_triples_matrix and n1 in freq_triples_matrix[n2] else 0
                l2l = (v1 + v2) / (v1 + v2 + 1)
                if l2l >= loops_length_two_thresh:
                    self.loop_length_two[n2] = c1

    def get_fill_color(self, default):
        """
        Gets the fill color for the representation

        Parameters
        --------------
        default
            Default value
        """
        if self.fill_color is not None:
            return self.fill_color
        return default

    def get_font_color(self):
        """
        Gets the font color for the representation
        """
        if self.font_color is not None:
            return self.font_color
        return "#000000"

    def __repr__(self):
        ret = "(node:" + self.node_name + " connections:{"
        for index, conn in enumerate(self.output_connections.keys()):
            if index > 0:
                ret = ret + ", "
            ret = ret + conn.node_name + ":" + str([x.dependency_value for x in self.output_connections[conn]])
        ret = ret + "})"
        return ret

    def __str__(self):
        return self.__repr__()

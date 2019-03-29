from pm4py.objects.heuristics_net import defaults
from pm4py.objects.heuristics_net.edge import Edge


class Node:
    def __init__(self, heuristics_net, node_name, node_occ, is_start_node=False, is_end_node=False,
                 default_edges_color="#000000", node_type="frequency", net_name=""):
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
                c3 = self.heuristics_net.dfg_matrix[self.node_name][n1]
                c4 = self.heuristics_net.dfg_matrix[self.node_name][n2]
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
                c3 = self.heuristics_net.dfg_matrix[n1][self.node_name]
                c4 = self.heuristics_net.dfg_matrix[n2][self.node_name]
                value = (c1 + c2) / (c3 + c4 + 1)
                if value >= and_measure_thresh:
                    if n1 not in self.and_measures_in:
                        self.and_measures_in[n1] = {}
                    self.and_measures_in[n1][n2] = value
                j = j + 1
            i = i + 1

    """def calculate_loops_length_two(self, loops_length_two_thresh=defaults.DEFAULT_LOOP_LENGTH_TWO_THRESH):
        out_nodes = sorted(list(self.output_connections), key=lambda x: x.node_name)
        for node in out_nodes:
            c1 = self.heuristics_net.dependency_matrix[self.node_name][node.node_name]
            c2 = self.heuristics_net.dependency_matrix[node.node_name][
                self.node_name] if node.node_name in self.heuristics_net.dependency_matrix and self.node_name in \
                                   self.heuristics_net.dependency_matrix[node.node_name] else 0
            l2l = (c1 + c2) / (c1 + c2 + 1)
            if l2l > loops_length_two_thresh:
                if self.node_name not in self.loop_length_two:
                    self.loop_length_two[self.node_name] = {}
                self.loop_length_two[self.node_name][node.node_name] = l2l"""

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

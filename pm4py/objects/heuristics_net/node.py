from pm4py.objects.heuristics_net.edge import Edge


class Node:
    def __init__(self, heuristics_net, node_name, node_occ, is_start_node=False, is_end_node=False):
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
        """
        self.heuristics_net = heuristics_net
        self.node_name = node_name
        self.node_occ = node_occ
        self.is_start_activity = is_start_node
        self.is_end_activity = is_end_node
        self.input_connections = {}
        self.output_connections = {}
        self.output_couples_and_measure = []

    def add_output_connection(self, other_node, dependency_value, dfg_value):
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
        """
        edge = Edge(self, other_node, dependency_value, dfg_value)
        self.output_connections[other_node] = edge

    def add_input_connection(self, other_node, dependency_value, dfg_value):
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
        """
        edge = Edge(self, other_node, dependency_value, dfg_value)
        self.input_connections[other_node] = edge

    def calculate_and_measure(self):
        pass

    def __repr__(self):
        ret = "(node:" + self.node_name + " connections:{"
        for index, conn in enumerate(self.output_connections.keys()):
            if index > 0:
                ret = ret + ", "
            ret = ret + conn.node_name + ":" + str(self.output_connections[conn].dependency_value)
        ret = ret + "})"
        return ret

    def __str__(self):
        return self.__repr__()

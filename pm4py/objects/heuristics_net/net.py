from copy import deepcopy

from pm4py.algo.discovery.dfg.utils import dfg_utils
from pm4py.algo.filtering.dfg.dfg_filtering import clean_dfg_based_on_noise_thresh
from pm4py.objects.heuristics_net import defaults
from pm4py.objects.heuristics_net.node import Node

DEFAULT_NET_NAME = ""


class HeuristicsNet:
    def __init__(self, frequency_dfg, activities=None, start_activities=None, end_activities=None,
                 activities_occurrences=None,
                 default_edges_color="#000000", performance_dfg=None, net_name=DEFAULT_NET_NAME):
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

    def calculate(self, dependency_thresh=defaults.DEFAULT_DEPENDENCY_THRESH,
                  and_measure_thresh=defaults.DEFAULT_AND_MEASURE_THRESH, min_act_count=defaults.DEFAULT_MIN_ACT_COUNT,
                  min_dfg_occurrences=defaults.DEFAULT_MIN_DFG_OCCURRENCES,
                  dfg_pre_cleaning_noise_thresh=defaults.DEFAULT_DFG_PRE_CLEANING_NOISE_THRESH,
                  loops_length_two_thresh=defaults.DEFAULT_LOOP_LENGTH_TWO_THRESH):
        """
        Calculate the dependency matrix, populate the nodes

        Parameters
        -------------
        dependency_thresh
            (Optional) dependency threshold
        and_measure_thresh
            (Optional) AND measure threshold
        min_act_count
            (Optional) minimum number of occurrences of an activity
        min_dfg_occurrences
            (Optional) minimum dfg occurrences
        dfg_pre_cleaning_noise_thresh
            (Optional) DFG pre cleaning noise threshold
        loops_length_two_thresh
            (Optional) loops length two threshold
        """
        self.dependency_matrix = None
        self.dependency_matrix = {}
        self.dfg_matrix = None
        self.dfg_matrix = {}
        self.performance_matrix = None
        self.performance_matrix = {}
        if dfg_pre_cleaning_noise_thresh > 0.0:
            self.dfg = clean_dfg_based_on_noise_thresh(self.dfg, self.activities, dfg_pre_cleaning_noise_thresh)
        for el in self.dfg:
            act1 = el[0]
            act2 = el[1]
            value = self.dfg[el]
            perf_value = self.performance_dfg[el] if self.performance_dfg is not None else self.dfg[el]
            if act1 not in self.dependency_matrix:
                self.dependency_matrix[act1] = {}
                self.dfg_matrix[act1] = {}
                self.performance_matrix[act1] = {}
            self.dfg_matrix[act1][act2] = value
            self.performance_matrix[act1][act2] = perf_value
            if not act1 == act2:
                inv_couple = (act2, act1)
                c1 = value
                if inv_couple in self.dfg:
                    c2 = self.dfg[inv_couple]
                    dep = (c1 - c2) / (c1 + c2 + 1)
                else:
                    dep = c1 / (c1 + 1)
            else:
                dep = value / (value + 1)
            self.dependency_matrix[act1][act2] = dep
        for n1 in self.dependency_matrix:
            for n2 in self.dependency_matrix[n1]:
                condition1 = n1 in self.activities_occurrences and self.activities_occurrences[n1] >= min_act_count
                condition2 = n2 in self.activities_occurrences and self.activities_occurrences[n2] >= min_act_count
                condition3 = self.dfg_matrix[n1][n2] >= min_dfg_occurrences
                condition4 = self.dependency_matrix[n1][n2] >= dependency_thresh
                condition = condition1 and condition2 and condition3 and condition4
                if condition:
                    if n1 not in self.nodes:
                        self.nodes[n1] = Node(self, n1, self.activities_occurrences[n1],
                                              is_start_node=(n1 in self.start_activities),
                                              is_end_node=(n1 in self.end_activities),
                                              default_edges_color=self.default_edges_color[0],
                                              node_type=self.node_type, net_name=self.net_name[0])
                    if n2 not in self.nodes:
                        self.nodes[n2] = Node(self, n2, self.activities_occurrences[n2],
                                              is_start_node=(n2 in self.start_activities),
                                              is_end_node=(n2 in self.end_activities),
                                              default_edges_color=self.default_edges_color[0],
                                              node_type=self.node_type, net_name=self.net_name[0])

                    repr_value = self.performance_matrix[n1][n2]
                    self.nodes[n1].add_output_connection(self.nodes[n2], self.dependency_matrix[n1][n2],
                                                         self.dfg_matrix[n1][n2], repr_value=repr_value)
                    self.nodes[n2].add_input_connection(self.nodes[n1], self.dependency_matrix[n1][n2],
                                                        self.dfg_matrix[n1][n2], repr_value=repr_value)
        for node in self.nodes:
            self.nodes[node].calculate_and_measure_out(and_measure_thresh=and_measure_thresh)
            self.nodes[node].calculate_and_measure_in(and_measure_thresh=and_measure_thresh)

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

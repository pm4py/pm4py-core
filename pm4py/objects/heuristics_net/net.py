from pm4py.algo.discovery.dfg.utils import dfg_utils
from pm4py.algo.filtering.dfg.dfg_filtering import clean_dfg_based_on_noise_thresh
from pm4py.objects.heuristics_net.node import Node


class HeuristicsNet:
    def __init__(self, dfg, activities=None, start_activities=None, end_activities=None, activities_occurrences=None,
                 default_edges_color="#000000"):
        """
        Initialize an Hueristics Net

        Parameters
        -------------
        dfg
            Directly-Follows graph
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

        """
        self.nodes = {}
        self.dependency_matrix = {}
        self.dfg_matrix = {}

        self.dfg = dfg
        self.activities = activities
        if self.activities is None:
            self.activities = dfg_utils.get_activities_from_dfg(dfg)
        self.start_activities = start_activities
        if self.start_activities is None:
            self.start_activities = dfg_utils.infer_start_activities(dfg)
        self.end_activities = end_activities
        if self.end_activities is None:
            self.end_activities = dfg_utils.infer_end_activities(dfg)
        self.activities_occurrences = activities_occurrences
        if self.activities_occurrences is None:
            self.activities_occurrences = {}
            for act in self.activities:
                self.activities_occurrences[act] = dfg_utils.sum_activities_count(dfg, [act])
        self.default_edges_color = default_edges_color

    def calculate(self, dependency_thresh=0.5, and_measure_thresh=0.75, min_act_count=0, min_dfg_occurrences=0,
                  dfg_pre_cleaning_noise_thresh=0.05):
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
        """
        self.dependency_matrix = None
        self.dependency_matrix = {}
        self.dfg_matrix = None
        self.dfg_matrix = {}
        if dfg_pre_cleaning_noise_thresh > 0.0:
            self.dfg = clean_dfg_based_on_noise_thresh(self.dfg, self.activities, dfg_pre_cleaning_noise_thresh)
        for el in self.dfg:
            act1 = el[0]
            act2 = el[1]
            value = self.dfg[el]
            if act1 not in self.dependency_matrix:
                self.dependency_matrix[act1] = {}
                self.dfg_matrix[act1] = {}
            self.dfg_matrix[act1][act2] = value
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
                condition1 = n1 in self.activities_occurrences and self.activities_occurrences[n1] > min_act_count
                condition2 = n2 in self.activities_occurrences and self.activities_occurrences[n2] > min_act_count
                condition3 = self.dfg_matrix[n1][n2] >= min_dfg_occurrences
                condition4 = self.dependency_matrix[n1][n2] >= dependency_thresh
                condition = condition1 and condition2 and condition3 and condition4
                if condition:
                    if n1 not in self.nodes:
                        self.nodes[n1] = Node(self, n1, self.activities_occurrences[n1],
                                              is_start_node=(n1 in self.start_activities),
                                              is_end_node=(n1 in self.end_activities),
                                              default_edges_color=self.default_edges_color)
                    if n2 not in self.nodes:
                        self.nodes[n2] = Node(self, n2, self.activities_occurrences[n2],
                                              is_start_node=(n2 in self.start_activities),
                                              is_end_node=(n2 in self.end_activities),
                                              default_edges_color=self.default_edges_color)
                    self.nodes[n1].add_output_connection(self.nodes[n2], self.dependency_matrix[n1][n2],
                                                         self.dfg_matrix[n1][n2])
                    self.nodes[n2].add_input_connection(self.nodes[n1], self.dependency_matrix[n1][n2],
                                                        self.dfg_matrix[n1][n2])
        for node in self.nodes:
            self.nodes[node].calculate_and_measure_out(and_measure_thresh=and_measure_thresh)

from copy import deepcopy, copy

import networkx as nx
import numpy as np

from pm4py.algo.discovery.dfg.utils.dfg_utils import filter_dfg_on_act
from pm4py.algo.discovery.dfg.utils.dfg_utils import get_all_activities_connected_as_input_to_activity
from pm4py.algo.discovery.dfg.utils.dfg_utils import get_all_activities_connected_as_output_to_activity
from pm4py.algo.discovery.dfg.utils.dfg_utils import get_connected_components, add_to_most_probable_component
from pm4py.algo.discovery.dfg.utils.dfg_utils import infer_end_activities_from_succ_connections_and_current_dfg
from pm4py.algo.discovery.dfg.utils.dfg_utils import infer_start_activities_from_prev_connections_and_current_dfg
from pm4py.algo.discovery.inductive.versions.dfg.data_structures.subtree_imdfa import Subtree


class SubtreeB(Subtree):
    def check_if_comp_is_completely_unconnected(self, conn1, conn2):
        """
        Checks if two connected components are completely unconnected each other

        Parameters
        -------------
        conn1
            First connected component
        conn2
            Second connected component

        Returns
        -------------
        boolean
            Boolean value that tells if the two connected components are completely unconnected
        """
        for act1 in conn1:
            for act2 in conn2:
                if ((act1 in self.outgoing and act2 in self.outgoing[act1]) and (
                        act1 in self.ingoing and act2 in self.ingoing[act1])):
                    return False
        return True

    def merge_connected_components(self, conn_components):
        """
        Merge the unconnected connected components

        Parameters
        -------------
        conn_components
            Connected components

        Returns
        -------------
        conn_components
            Merged connected components
        """
        i = 0
        while i < len(conn_components):
            conn1 = conn_components[i]
            j = i + 1
            while j < len(conn_components):
                conn2 = conn_components[j]
                if self.check_if_comp_is_completely_unconnected(conn1, conn2):
                    conn_components[i] = set(conn_components[i]).union(set(conn_components[j]))
                    del conn_components[j]
                    continue
                j = j + 1
            i = i + 1
        return conn_components

    def check_par_cut(self, conn_components, this_nx_graph, strongly_connected_components):
        """
        Checks if in a parallel cut all relations are present

        Parameters
        -----------
        conn_components
            Connected components
        this_nx_graph
            NX graph calculated on the DFG
        strongly_connected_components
            Strongly connected components
        """
        conn_components = self.merge_connected_components(conn_components)
        i = 0
        while i < len(conn_components):
            conn1 = conn_components[i]
            j = i + 1
            while j < len(conn_components):
                conn2 = conn_components[j]
                for act1 in conn1:
                    for act2 in conn2:
                        if not ((act1 in self.outgoing and act2 in self.outgoing[act1]) and (
                                act1 in self.ingoing and act2 in self.ingoing[act1])):
                            return False
                j = j + 1
            i = i + 1
        if len(conn_components) > 1:
            return True
        return False

    def detect_loop_cut(self, conn_components, this_nx_graph, strongly_connected_components):
        """
        Detect loop cut

        Parameters
        --------------
        conn_components
            Connected components of the graph
        this_nx_graph
            NX graph calculated on the DFG
        strongly_connected_components
            Strongly connected components
        """
        start_activities = self.start_activities
        if len(start_activities) == 0:
            start_activities = infer_start_activities_from_prev_connections_and_current_dfg(self.initial_dfg, self.dfg,
                                                                                            self.activities)
        end_activities = self.end_activities

        end_activities = list(set(end_activities) - set(start_activities))

        if len(end_activities) == 0:
            end_activities = infer_end_activities_from_succ_connections_and_current_dfg(self.initial_dfg, self.dfg,
                                                                                        self.activities)
            end_activities = list(set(end_activities) - set(start_activities))
            if len(end_activities) == 0:
                end_activities = infer_end_activities_from_succ_connections_and_current_dfg(self.initial_dfg, self.dfg,
                                                                                            self.activities,
                                                                                            include_self=False)
        all_end_activities = deepcopy(end_activities)
        end_activities = list(set(end_activities) - set(start_activities))
        end_activities_that_are_also_start = list(set(all_end_activities) - set(end_activities))

        do_part = []
        redo_part = []
        dangerous_redo_part = []
        exit_part = []

        for sa in start_activities:
            do_part.append(sa)
        for ea in end_activities:
            exit_part.append(ea)

        for act in self.activities:
            if act not in start_activities and act not in end_activities:
                input_connected_activities = get_all_activities_connected_as_input_to_activity(self.dfg, act)
                output_connected_activities = get_all_activities_connected_as_output_to_activity(self.dfg, act)
                if output_connected_activities.issubset(start_activities) and start_activities.issubset(
                        output_connected_activities):
                    if len(input_connected_activities.intersection(exit_part)) > 0:
                        dangerous_redo_part.append(act)
                    redo_part.append(act)
                else:
                    do_part.append(act)

        if len(do_part) > 0 and (len(redo_part) > 0 or len(exit_part)) > 0:
            # print([True, [do_part, redo_part + exit_part, set()], len(end_activities_that_are_also_start) > 0])
            return [True, [do_part, redo_part + exit_part, set()], len(end_activities_that_are_also_start) > 0]

        return [False, [], []]

    def get_connection_matrix(self, strongly_connected_components):
        """
        Gets the connection matrix between connected components

        Parameters
        ------------
        strongly_connected_components
            Strongly connected components

        Returns
        ------------
        connection_matrix
            Matrix reporting the connections
        """
        act_to_scc = {}
        for index, comp in enumerate(strongly_connected_components):
            for act in comp:
                act_to_scc[act] = index
        conn_matrix = np.zeros((len(strongly_connected_components), len(strongly_connected_components)))
        for el in self.dfg:
            comp_el_0 = act_to_scc[el[0][0]]
            comp_el_1 = act_to_scc[el[0][1]]
            if not comp_el_0 == comp_el_1:
                conn_matrix[comp_el_1][comp_el_0] = 1
                if conn_matrix[comp_el_0][comp_el_1] == 0:
                    conn_matrix[comp_el_0][comp_el_1] = -1
        return conn_matrix

    def detect_sequential_cut(self, conn_components, this_nx_graph, strongly_connected_components):
        """
        Detect sequential cut in DFG graph

        Parameters
        --------------
        conn_components
            Connected components of the graph
        this_nx_graph
            NX graph calculated on the DFG
        strongly_connected_components
            Strongly connected components
        """
        if len(strongly_connected_components) > 1:
            orig_conn_comp = copy(strongly_connected_components)
            conn_matrix = self.get_connection_matrix(strongly_connected_components)
            something_changed = True
            while something_changed:
                something_changed = False
                i = 0
                while i < len(strongly_connected_components):
                    idx_i_comp = orig_conn_comp.index(strongly_connected_components[i])
                    j = i + 1
                    while j < len(strongly_connected_components):
                        idx_j_comp = orig_conn_comp.index(strongly_connected_components[j])
                        if conn_matrix[idx_i_comp][idx_j_comp] > 0:
                            copyel = copy(strongly_connected_components[i])
                            strongly_connected_components[i] = strongly_connected_components[j]
                            strongly_connected_components[j] = copyel
                            something_changed = True
                            break
                        j = j + 1
                    i = i + 1
            ret_connected_components = []
            ignore_comp = set()
            i = 0
            while i < len(strongly_connected_components):
                if i not in ignore_comp:
                    idx_i_comp = orig_conn_comp.index(strongly_connected_components[i])
                    comp = copy(strongly_connected_components[i])
                    j = i + 1
                    is_component_mergeable = True
                    while j < len(strongly_connected_components):
                        idx_j_comp = orig_conn_comp.index(strongly_connected_components[j])
                        if conn_matrix[idx_i_comp][idx_j_comp] < 0 or conn_matrix[idx_i_comp][idx_j_comp] > 0:
                            is_component_mergeable = False
                            break
                        j = j + 1
                    if is_component_mergeable:
                        j = i + 1
                        while j < len(strongly_connected_components):
                            idx_j_comp = orig_conn_comp.index(strongly_connected_components[j])
                            if conn_matrix[idx_i_comp][idx_j_comp] == 0:
                                comp = comp + strongly_connected_components[j]
                                ignore_comp.add(j)
                            else:
                                break
                            j = j + 1
                    ret_connected_components.append(comp)
                i = i + 1

            if len(ret_connected_components) > 1:
                return [True, ret_connected_components]
        return [False, [], []]

    def transform_dfg_to_directed_nx_graph(self):
        """
        Transform DFG to directed NetworkX graph

        Returns
        ------------
        G
            NetworkX digraph
        nodes_map
            Correspondence between digraph nodes and activities
        """
        G = nx.DiGraph()
        for act in self.activities:
            G.add_node(act)
        for el in self.dfg:
            act1 = el[0][0]
            act2 = el[0][1]
            G.add_edge(act1, act2)
        return G

    def detect_cut(self, second_iteration=False):
        """
        Detect generally a cut in the graph (applying all the algorithms)
        """
        if self.dfg:
            # print("\n\n")
            conn_components = get_connected_components(self.ingoing, self.outgoing, self.activities)
            this_nx_graph = self.transform_dfg_to_directed_nx_graph()
            strongly_connected_components = [list(x) for x in nx.strongly_connected_components(this_nx_graph)]

            # print("strongly_connected_components", strongly_connected_components)

            conc_cut = self.detect_concurrent_cut(conn_components, this_nx_graph, strongly_connected_components)
            seq_cut = self.detect_sequential_cut(conn_components, this_nx_graph, strongly_connected_components)
            par_cut = self.detect_parallel_cut(conn_components, this_nx_graph, strongly_connected_components)
            loop_cut = self.detect_loop_cut(conn_components, this_nx_graph, strongly_connected_components)

            if conc_cut[0]:
                # print(self.rec_depth, "conc_cut", self.activities)
                for comp in conc_cut[1]:
                    new_dfg = filter_dfg_on_act(self.dfg, comp)
                    self.detected_cut = "concurrent"
                    self.children.append(
                        SubtreeB(new_dfg, self.master_dfg, self.initial_dfg, comp, self.counts, self.rec_depth + 1,
                                 noise_threshold=self.noise_threshold))
            else:
                if seq_cut[0]:
                    # print(self.rec_depth, "seq_cut", self.activities)
                    self.detected_cut = "sequential"
                    for child in seq_cut[1]:
                        dfg_child = filter_dfg_on_act(self.dfg, child)
                        self.children.append(
                            SubtreeB(dfg_child, self.master_dfg, self.initial_dfg, child, self.counts,
                                     self.rec_depth + 1,
                                     noise_threshold=self.noise_threshold))
                else:
                    if par_cut[0]:
                        # print(self.rec_depth, "par_cut", self.activities, par_cut[1])
                        union_acti_comp = set()
                        for comp in par_cut[1]:
                            union_acti_comp = union_acti_comp.union(comp)
                        diff_acti_comp = set(self.activities).difference(union_acti_comp)

                        for act in diff_acti_comp:
                            par_cut[1] = add_to_most_probable_component(par_cut[1], act, self.ingoing, self.outgoing)

                        for comp in par_cut[1]:
                            new_dfg = filter_dfg_on_act(self.dfg, comp)
                            self.detected_cut = "parallel"
                            self.children.append(
                                SubtreeB(new_dfg, self.master_dfg, new_dfg, comp, self.counts,
                                         self.rec_depth + 1,
                                         noise_threshold=self.noise_threshold))
                    else:
                        if loop_cut[0]:
                            # print(self.rec_depth, "loop_cut", self.activities, loop_cut)
                            self.detected_cut = "loopCut"
                            for index_enum, child in enumerate(loop_cut[1]):
                                dfg_child = filter_dfg_on_act(self.dfg, child)
                                next_subtree = SubtreeB(dfg_child, self.master_dfg, self.initial_dfg, child,
                                                        self.counts, self.rec_depth + 1,
                                                        noise_threshold=self.noise_threshold)
                                if loop_cut[2] and index_enum > 0:
                                    next_subtree.force_loop_hidden = True
                                self.children.append(next_subtree)
                        else:
                            if self.noise_threshold > 0:
                                if not second_iteration:
                                    self.initialize_tree(self.dfg, self.initial_dfg, None, second_iteration=True)
                            else:
                                pass
                            self.detected_cut = "flower"
        else:
            self.detected_cut = "base_concurrent"

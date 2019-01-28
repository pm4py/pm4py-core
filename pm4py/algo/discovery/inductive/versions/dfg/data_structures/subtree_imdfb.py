import networkx as nx

from pm4py.algo.discovery.dfg.utils.dfg_utils import filter_dfg_on_act
from pm4py.algo.discovery.dfg.utils.dfg_utils import get_connected_components, add_to_most_probable_component
from pm4py.algo.discovery.dfg.utils.dfg_utils import infer_end_activities
from pm4py.algo.discovery.dfg.utils.dfg_utils import infer_start_activities
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
                            if self.check_if_comp_is_completely_unconnected(conn1, conn2):
                                conn_components[i] = list(set(conn_components[i] + conn_components[j]))
                                del conn_components[j]
                                continue
                            else:
                                return False
                j = j + 1
            i = i + 1
        return True

    def infer_start_activities_from_prev_connections_and_current_dfg(self, initial_dfg, dfg, activities):
        """
        Infer the start activities from the previous connections
        """
        start_activities = set()
        for el in initial_dfg:
            if el[0][1] in self.activities and not el[0][0] in activities:
                start_activities.add(el[0][1])
        start_activities = start_activities.union(set(infer_start_activities(dfg)))
        return start_activities

    def infer_end_activities_from_succ_connections_and_current_dfg(self, initial_dfg, dfg, activities):
        """
        Infer the end activities from the previous connections
        """
        end_activities = set()
        for el in initial_dfg:
            if el[0][0] in activities and not el[0][1] in activities:
                end_activities.add(el[0][0])
        end_activities = end_activities.union(set(infer_end_activities(dfg)))
        return end_activities

    def get_all_activities_connected_as_output_to_activity(self, activity):
        """
        Gets all the activities that are connected as output to a given activity

        Parameters
        -------------
        activity
            Activity

        Returns
        -------------
        all_activities
            All activities connected as output to a given activity
        """
        all_activities = set()

        for el in self.dfg:
            if el[0][0] == activity:
                all_activities.add(el[0][1])

        return all_activities

    def get_all_activities_connected_as_input_to_activity(self, activity):
        """
        Gets all the activities that are connected as input to a given activity

        Parameters
        ------------
        activity
            Activity

        Returns
        ------------
        all_activities
            All activities connected as input to a given activities
        """
        all_activities = set()
        for el in self.dfg:
            if el[0][1] == activity:
                all_activities.add(el[0][0])
        return all_activities

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
        start_activities = self.infer_start_activities_from_prev_connections_and_current_dfg(self.initial_dfg, self.dfg,
                                                                                             self.activities)
        end_activities = self.infer_end_activities_from_succ_connections_and_current_dfg(self.initial_dfg, self.dfg,
                                                                                         self.activities)
        end_activities = end_activities - start_activities

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
                input_connected_activities = self.get_all_activities_connected_as_input_to_activity(act)
                output_connected_activities = self.get_all_activities_connected_as_output_to_activity(act)
                if output_connected_activities.issubset(start_activities) and start_activities.issubset(
                        output_connected_activities):
                    if len(input_connected_activities.intersection(exit_part)) > 0:
                        dangerous_redo_part.append(act)
                    redo_part.append(act)
                else:
                    do_part.append(act)

        if len(redo_part) > 0 or len(exit_part) > 0:
            if dangerous_redo_part:
                return [True, [do_part, redo_part + exit_part, set()]]
            else:
                return [True, [do_part, redo_part, exit_part]]

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
            strongly_connected_components = list(nx.strongly_connected_components(this_nx_graph))

            conc_cut = self.detect_concurrent_cut(conn_components, this_nx_graph, strongly_connected_components)
            seq_cut = self.detect_sequential_cut(conn_components, this_nx_graph, strongly_connected_components)
            par_cut = self.detect_parallel_cut(conn_components, this_nx_graph, strongly_connected_components)
            loop_cut = self.detect_loop_cut(conn_components, this_nx_graph, strongly_connected_components)

            if conc_cut[0]:
                for comp in conc_cut[1]:
                    new_dfg = filter_dfg_on_act(self.dfg, comp)
                    self.detected_cut = "concurrent"
                    self.children.append(SubtreeB(new_dfg, self.initial_dfg, comp, self.counts, self.rec_depth + 1,
                                                  noise_threshold=self.noise_threshold))
            else:
                if seq_cut[0]:
                    self.detected_cut = "sequential"
                    for child in seq_cut[1]:
                        dfg_child = filter_dfg_on_act(self.dfg, child)
                        self.children.append(
                            SubtreeB(dfg_child, self.initial_dfg, child, self.counts, self.rec_depth + 1,
                                     noise_threshold=self.noise_threshold))
                else:
                    if par_cut[0]:
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
                                SubtreeB(new_dfg, self.initial_dfg, comp, self.counts, self.rec_depth + 1,
                                         noise_threshold=self.noise_threshold))
                    else:
                        if loop_cut[0]:
                            self.detected_cut = "loopCut"
                            for child in loop_cut[1]:
                                dfg_child = filter_dfg_on_act(self.dfg, child)
                                self.children.append(
                                    SubtreeB(dfg_child, self.initial_dfg, child, self.counts, self.rec_depth + 1,
                                             noise_threshold=self.noise_threshold))
                        else:
                            if self.noise_threshold > 0:
                                if not second_iteration:
                                    self.initialize_tree(self.dfg, self.initial_dfg, None, second_iteration=True)
                            else:
                                pass
                            self.detected_cut = "flower"
        else:
            self.detected_cut = "base_concurrent"

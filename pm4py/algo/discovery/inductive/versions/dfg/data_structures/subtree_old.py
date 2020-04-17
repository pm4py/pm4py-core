import numpy as np

from copy import copy

from pm4py.objects.dfg.utils.dfg_utils import get_all_activities_connected_as_input_to_activity
from pm4py.objects.dfg.utils.dfg_utils import get_all_activities_connected_as_output_to_activity
from pm4py.objects.dfg.utils.dfg_utils import filter_dfg_on_act, negate, get_activities_dirlist, \
    get_activities_self_loop, get_activities_direction
from pm4py.objects.dfg.utils.dfg_utils import get_ingoing_edges, get_outgoing_edges, get_activities_from_dfg, \
    infer_start_activities, infer_end_activities
from pm4py.objects.dfg.filtering.dfg_filtering import clean_dfg_based_on_noise_thresh
from pm4py.objects.dfg.utils.dfg_utils import infer_start_activities_from_prev_connections_and_current_dfg, \
    infer_end_activities_from_succ_connections_and_current_dfg


class SubtreeDFGBasedOld():
    def __init__(self, dfg, master_dfg, initial_dfg, activities, counts, rec_depth, noise_threshold=0,
                 start_activities=None, end_activities=None, initial_start_activities=None,
                 initial_end_activities=None):
        """
        Constructor

        Parameters
        -----------
        dfg
            Directly follows graph of this subtree
        master_dfg
            Original DFG
        initial_dfg
            Referral directly follows graph that should be taken in account adding hidden/loop transitions
        activities
            Activities of this subtree
        counts
            Shared variable
        rec_depth
            Current recursion depth
        """
        self.master_dfg = copy(master_dfg)
        self.initial_dfg = copy(initial_dfg)
        self.counts = counts
        self.rec_depth = rec_depth
        self.noise_threshold = noise_threshold
        self.start_activities = start_activities
        if self.start_activities is None:
            self.start_activities = []
        self.end_activities = end_activities
        if self.end_activities is None:
            self.end_activities = []
        self.initial_start_activities = initial_start_activities
        if self.initial_start_activities is None:
            self.initial_start_activities = infer_start_activities(master_dfg)
        self.initial_end_activities = initial_end_activities
        if self.initial_end_activities is None:
            self.initial_end_activities = infer_end_activities(master_dfg)

        self.second_iteration = None
        self.activities = None
        self.dfg = None
        self.outgoing = None
        self.ingoing = None
        self.self_loop_activities = None
        self.initial_ingoing = None
        self.initial_outgoing = None
        self.activities_direction = None
        self.activities_dir_list = None
        self.negated_dfg = None
        self.negated_activities = None
        self.negated_outgoing = None
        self.negated_ingoing = None
        self.detected_cut = None
        self.children = None
        self.must_insert_skip = False
        self.need_loop_on_subtree = False

        self.initialize_tree(dfg, initial_dfg, activities)

    def initialize_tree(self, dfg, initial_dfg, activities, second_iteration=False):
        """
        Initialize the tree


        Parameters
        -----------
        dfg
            Directly follows graph of this subtree
        initial_dfg
            Referral directly follows graph that should be taken in account adding hidden/loop transitions
        activities
            Activities of this subtree
        second_iteration
            Boolean that indicates if we are executing this method for the second time
        """

        self.second_iteration = second_iteration

        if activities is None:
            self.activities = get_activities_from_dfg(dfg)
        else:
            self.activities = copy(activities)

        if second_iteration:
            self.dfg = clean_dfg_based_on_noise_thresh(self.dfg, self.activities, self.noise_threshold)
        else:
            self.dfg = copy(dfg)

        self.initial_dfg = initial_dfg

        self.outgoing = get_outgoing_edges(self.dfg)
        self.ingoing = get_ingoing_edges(self.dfg)
        self.self_loop_activities = get_activities_self_loop(self.dfg)
        self.initial_outgoing = get_outgoing_edges(self.initial_dfg)
        self.initial_ingoing = get_ingoing_edges(self.initial_dfg)
        self.activities_direction = get_activities_direction(self.dfg, self.activities)
        self.activities_dir_list = get_activities_dirlist(self.activities_direction)
        self.negated_dfg = negate(self.dfg)
        self.negated_activities = get_activities_from_dfg(self.negated_dfg)
        self.negated_outgoing = get_outgoing_edges(self.negated_dfg)
        self.negated_ingoing = get_ingoing_edges(self.negated_dfg)
        self.detected_cut = None
        self.children = []

        self.detect_cut(second_iteration=second_iteration)

    def get_connected_components(self, ingoing, outgoing, activities):
        """
        Get connected components in the DFG graph

        Parameters
        -----------
        ingoing
            Ingoing attributes
        outgoing
            Outgoing attributes
        activities
            Activities to consider
        """
        activities_considered = set()

        connected_components = []

        for act in ingoing:
            ingoing_act = set(ingoing[act].keys())
            if act in outgoing:
                ingoing_act = ingoing_act.union(set(outgoing[act].keys()))

            ingoing_act.add(act)

            if ingoing_act not in connected_components:
                connected_components.append(ingoing_act)
                activities_considered = activities_considered.union(set(ingoing_act))

        for act in outgoing:
            if act not in ingoing:
                outgoing_act = set(outgoing[act].keys())
                outgoing_act.add(act)
                if outgoing_act not in connected_components:
                    connected_components.append(outgoing_act)
                activities_considered = activities_considered.union(set(outgoing_act))

        for activ in activities:
            if activ not in activities_considered:
                added_set = set()
                added_set.add(activ)
                connected_components.append(added_set)
                activities_considered.add(activ)

        max_it = len(connected_components)
        for it in range(max_it - 1):
            something_changed = False

            old_connected_components = copy(connected_components)
            connected_components = []

            for i in range(len(old_connected_components)):
                conn1 = old_connected_components[i]

                if conn1 is not None:
                    for j in range(i + 1, len(old_connected_components)):
                        conn2 = old_connected_components[j]
                        if conn2 is not None:
                            inte = conn1.intersection(conn2)

                            if len(inte) > 0:
                                conn1 = conn1.union(conn2)
                                something_changed = True
                                old_connected_components[j] = None

                if conn1 is not None and conn1 not in connected_components:
                    connected_components.append(conn1)

            if not something_changed:
                break

        return connected_components

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
        conn_components = sorted(conn_components, key=lambda x: len(x))
        sthing_changed = True
        while sthing_changed:
            sthing_changed = False
            i = 0
            while i < len(conn_components):
                ok_comp_idx = []
                partly_ok_comp_idx = []
                not_ok_comp_idx = []
                conn1 = conn_components[i]
                j = i + 1
                while j < len(conn_components):
                    count_good = 0
                    count_notgood = 0
                    conn2 = conn_components[j]
                    for act1 in conn1:
                        for act2 in conn2:
                            if not ((act1 in self.outgoing and act2 in self.outgoing[act1]) and (
                                    act1 in self.ingoing and act2 in self.ingoing[act1])):
                                count_notgood = count_notgood + 1
                                if count_good > 0:
                                    break
                            else:
                                count_good = count_good + 1
                                if count_notgood > 0:
                                    break
                    if count_notgood == 0:
                        ok_comp_idx.append(j)
                    elif count_good > 0:
                        partly_ok_comp_idx.append(j)
                    else:
                        not_ok_comp_idx.append(j)
                    j = j + 1
                if not_ok_comp_idx or partly_ok_comp_idx:
                    if partly_ok_comp_idx:
                        conn_components[i] = set(conn_components[i]).union(set(conn_components[partly_ok_comp_idx[0]]))
                        del conn_components[partly_ok_comp_idx[0]]
                        sthing_changed = True
                        continue
                    else:
                        return False
                if sthing_changed:
                    break
                i = i + 1
        if len(conn_components) > 1:
            return conn_components
        return None

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
        all_end_activities = copy(end_activities)
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
                if set(output_connected_activities).issubset(start_activities) and set(start_activities).issubset(
                        output_connected_activities):
                    if len(input_connected_activities.intersection(exit_part)) > 0:
                        dangerous_redo_part.append(act)
                    redo_part.append(act)
                else:
                    do_part.append(act)

        if len(do_part) > 0 and (len(redo_part) > 0 or len(exit_part)) > 0:
            if len(redo_part) > 0:
                return [True, [do_part + exit_part, redo_part], len(end_activities_that_are_also_start) > 0]
            else:
                return [True, [do_part, redo_part + exit_part], len(end_activities_that_are_also_start) > 0]

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
                    else:
                        j = i + 1
                        while j < len(strongly_connected_components):
                            idx_j_comp = orig_conn_comp.index(strongly_connected_components[j])
                            # two components that have exactly the same inputs/outputs are merged
                            if np.array_equal(conn_matrix[idx_i_comp], conn_matrix[idx_j_comp]):
                                comp = comp + strongly_connected_components[j]
                                ignore_comp.add(j)
                            j = j + 1
                    ret_connected_components.append(comp)
                i = i + 1

            if len(ret_connected_components) > 1:
                return [True, ret_connected_components]
        return [False, [], []]

    def detect_xor_cut(self, conn_components, this_nx_graph, strongly_connected_components):
        """
        Detects XOR cut

        Parameters
        --------------
        conn_components
            Connected components
        this_nx_graph
            NX graph calculated on the DFG
        strongly_connected_components
            Strongly connected components
        """
        if len(self.dfg) > 0:
            if len(conn_components) > 1:
                return [True, conn_components]

        return [False, []]

    def detect_parallel_cut(self, orig_conn_components, this_nx_graph, strongly_connected_components):
        """
        Detects parallel cut

        Parameters
        --------------
        orig_conn_components
            Connected components of the graph
        this_nx_graph
            NX graph calculated on the DFG
        strongly_connected_components
            Strongly connected components
        """
        conn_components = self.get_connected_components(self.negated_ingoing, self.negated_outgoing, self.activities)

        if len(conn_components) > 1:
            conn_components = self.check_par_cut(conn_components, this_nx_graph, strongly_connected_components)
            if conn_components is not None:
                #print("\n", conn_components, self.initial_dfg)
                for comp in conn_components:
                    # print(self.rec_depth, comp)
                    comp_ok = False
                    for el in self.initial_dfg:
                        #print(el[0][0], comp, el[0][0] in comp)
                        #print(el[0][1], self.activities, el[0][1] not in self.activities)
                        #print(el[0][1], comp, el[0][1] in comp)
                        #print(el[0][0], self.activities, el[0][0] not in self.activities)
                        if (el[0][0] in comp and el[0][1] not in self.activities) or (
                                el[0][1] in comp and el[0][0] not in self.activities):
                            comp_ok = True
                            break
                    if self.rec_depth == 0:
                        for sa in self.start_activities:
                            if sa in comp:
                                comp_ok = True
                                #print("siii")
                                break
                    if not comp_ok:
                        return [False, conn_components]
                return [True, conn_components]

        return [False, []]

    def __str__(self):
        return "subtree rec_depth="+str(self.rec_depth)+" dfg="+str(self.dfg)+" activities="+str(self.activities)

    def __repr__(self):
        return "subtree rec_depth="+str(self.rec_depth)+" dfg="+str(self.dfg)+" activities="+str(self.activities)

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
        import networkx as nx

        G = nx.DiGraph()
        for act in self.activities:
            G.add_node(act)
        for el in self.dfg:
            act1 = el[0][0]
            act2 = el[0][1]
            G.add_edge(act1, act2)
        return G

    def put_skips_in_seq_cut(self):
        """
        Puts the skips in sequential cut
        """
        # first, put skips when in some cut there is an ending activity
        in_end_act = set(self.initial_end_activities)
        i = 0
        while i < len(self.children) - 1:
            activities_set = set(self.children[i].activities)
            intersection = activities_set.intersection(in_end_act)
            if len(intersection) > 0:
                j = i + 1
                while j < len(self.children):
                    self.children[j].must_insert_skip = True
                    j = j + 1
            i = i + 1

        # second, put skips when in some cut you are not sure to pass through
        i = 0
        while i < len(self.children) - 1:
            act_i = self.children[i].activities
            act_i_output_appearences = {}
            max_value = i
            for act in act_i:
                for out_act in self.outgoing[act]:
                    act_i_output_appearences[out_act] = len(self.children) - 1
            j = i + 1
            while j < len(self.children):
                act_children = self.children[j].activities
                for act in act_children:
                    if act in act_i_output_appearences and act_i_output_appearences[act] == len(self.children) - 1:
                        act_i_output_appearences[act] = j
                        if j > max_value:
                            max_value = j
                j = j + 1
            j = i + 1
            while j < max_value:
                self.children[j].must_insert_skip = True
                j = j + 1
            i = i + 1

        this_start_activities = set(infer_start_activities(self.dfg))
        # third, put skips when some input activities do not pass there
        out_start_activities = infer_start_activities_from_prev_connections_and_current_dfg(self.initial_dfg, self.dfg,
                                                                                            self.activities,
                                                                                            include_self=False)
        out_start_activities_diff = out_start_activities - set(self.activities)
        for act in out_start_activities_diff:
            out_act_here = set()
            for el in self.initial_dfg:
                if el[0][0] == act and el[0][1] in self.activities:
                    out_act_here.add(el[0][1])
            i = 0
            while i < len(self.children):
                child_act = set(self.children[i].activities)
                inte = child_act.intersection(out_act_here)
                if inte:
                    for el in inte:
                        out_act_here.remove(el)
                if len(out_act_here) > 0:
                    self.children[i].must_insert_skip = True
                i = i + 1

        # fourth, put skips until all start activities are reached
        remaining_act = (out_start_activities - this_start_activities).intersection(self.activities)
        i = 0
        while i < len(self.children):
            child_act = set(self.children[i].activities)
            inte = child_act.intersection(remaining_act)
            if inte:
                for el in inte:
                    remaining_act.remove(el)
            if len(remaining_act) > 0:
                self.children[i].must_insert_skip = True
            i = i + 1

    def put_skips_in_loop_cut(self):
        """
        Puts the skips in loop cuts
        """
        all_start_activities = infer_start_activities_from_prev_connections_and_current_dfg(self.initial_dfg, self.dfg,
                                                                                            self.activities)
        if not all_start_activities:
            self.children[0].must_insert_skip = True
            self.children[1].must_insert_skip = True
            return

    def detect_cut(self, second_iteration=False):
        """
        Detect generally a cut in the graph (applying all the algorithms)
        """
        import networkx as nx

        if self.dfg:
            # print("\n\n")
            conn_components = self.get_connected_components(self.ingoing, self.outgoing, self.activities)
            this_nx_graph = self.transform_dfg_to_directed_nx_graph()
            strongly_connected_components = [list(x) for x in nx.strongly_connected_components(this_nx_graph)]

            xor_cut = self.detect_xor_cut(conn_components, this_nx_graph, strongly_connected_components)

            if xor_cut[0]:
                for comp in xor_cut[1]:
                    new_dfg = filter_dfg_on_act(self.dfg, comp)
                    self.detected_cut = "xor"
                    self.children.append(
                        SubtreeDFGBasedOld(new_dfg, self.master_dfg, self.initial_dfg, comp, self.counts, self.rec_depth + 1,
                                           noise_threshold=self.noise_threshold,
                                           initial_start_activities=self.initial_start_activities,
                                           initial_end_activities=self.initial_end_activities))
            else:
                seq_cut = self.detect_sequential_cut(conn_components, this_nx_graph, strongly_connected_components)
                if seq_cut[0]:
                    # print(self.rec_depth, "seq_cut", self.activities)
                    self.detected_cut = "sequential"
                    for child in seq_cut[1]:
                        dfg_child = filter_dfg_on_act(self.dfg, child)
                        self.children.append(
                            SubtreeDFGBasedOld(dfg_child, self.master_dfg, self.initial_dfg, child, self.counts,
                                               self.rec_depth + 1,
                                               noise_threshold=self.noise_threshold,
                                               initial_start_activities=self.initial_start_activities,
                                               initial_end_activities=self.initial_end_activities))
                    self.put_skips_in_seq_cut()
                else:
                    par_cut = self.detect_parallel_cut(conn_components, this_nx_graph, strongly_connected_components)
                    if par_cut[0]:
                        self.detected_cut = "parallel"
                        for comp in par_cut[1]:
                            new_dfg = filter_dfg_on_act(self.dfg, comp)
                            self.children.append(
                                SubtreeDFGBasedOld(new_dfg, self.master_dfg, new_dfg, comp, self.counts,
                                                   self.rec_depth + 1,
                                                   noise_threshold=self.noise_threshold,
                                                   initial_start_activities=self.initial_start_activities,
                                                   initial_end_activities=self.initial_end_activities))
                    else:
                        loop_cut = self.detect_loop_cut(conn_components, this_nx_graph, strongly_connected_components)
                        if loop_cut[0]:
                            # print(self.rec_depth, "loop_cut", self.activities, loop_cut)
                            self.detected_cut = "loopCut"
                            for index_enum, child in enumerate(loop_cut[1]):
                                dfg_child = filter_dfg_on_act(self.dfg, child)
                                next_subtree = SubtreeDFGBasedOld(dfg_child, self.master_dfg, self.initial_dfg, child,
                                                                  self.counts, self.rec_depth + 1,
                                                                  noise_threshold=self.noise_threshold,
                                                                  initial_start_activities=self.initial_start_activities,
                                                                  initial_end_activities=self.initial_end_activities)
                                if loop_cut[2] and index_enum > 0:
                                    next_subtree.force_loop_hidden = True
                                self.children.append(next_subtree)
                            self.put_skips_in_loop_cut()
                        else:
                            if self.noise_threshold > 0:
                                if not second_iteration:
                                    self.initialize_tree(self.dfg, self.initial_dfg, None, second_iteration=True)
                            else:
                                pass
                            self.detected_cut = "flower"
        else:
            self.detected_cut = "base_xor"

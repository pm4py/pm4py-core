from copy import copy

from pm4py.algo.discovery.dfg.utils.dfg_utils import filter_dfg_on_act, negate, get_activities_dirlist, \
    get_activities_self_loop, get_activities_direction
from pm4py.algo.discovery.dfg.utils.dfg_utils import get_ingoing_edges, get_outgoing_edges, get_activities_from_dfg, \
    get_connected_components, add_to_most_probable_component, infer_start_activities, infer_end_activities
from pm4py.algo.discovery.inductive.util import shared_constants
from pm4py.algo.filtering.dfg.dfg_filtering import clean_dfg_based_on_noise_thresh


class Subtree(object):
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

    def determine_best_set_sequential(self, act, set1, set2, preferred_set1):
        """
        Determine best set to assign the current activity

        Parameters
        -----------
        act
            Activity
        set1
            First set of attributes
        set2
            Second set of attributes
        preferred_set1
            Boolean value that decides if activities goes preferrely in set1 or in set2
        """
        has_outgoing_conn_set1 = False
        if act[0] in self.outgoing:
            for act2 in self.outgoing[act[0]]:
                if act2 in set1:
                    has_outgoing_conn_set1 = True
        has_ingoing_conn_set2 = False
        if act[0] in self.ingoing:
            for act2 in self.ingoing[act[0]]:
                if act2 in set2:
                    has_ingoing_conn_set2 = True

        if has_outgoing_conn_set1 and has_ingoing_conn_set2:
            return [False, set1, set2]

        if has_outgoing_conn_set1:
            set1.add(act[0])
        elif has_ingoing_conn_set2:
            set2.add(act[0])
        else:
            if (preferred_set1 or act[1] < shared_constants.SEQ_SET2_CONST) and not (
                    act[1] > shared_constants.SEQ_SET1_CONST):
                set2.add(act[0])
            else:
                set1.add(act[0])

        return [True, set1, set2]

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
        set1 = set()
        set2 = set()

        if len(self.activities_dir_list) > 0:
            set1.add(self.activities_dir_list[0][0])
            if not (self.activities_dir_list[0][0] in self.ingoing and self.activities_dir_list[-1][0] in self.ingoing[
                self.activities_dir_list[0][0]]):
                set2.add(self.activities_dir_list[-1][0])
            else:
                return [False, [], []]

            preferred_set1 = abs(self.activities_dir_list[0][1]) > abs(self.activities_dir_list[-1][1])

            for i in range(1, len(self.activities_dir_list) - 1):
                act = self.activities_dir_list[i]
                ret, set1, set2 = self.determine_best_set_sequential(act, set1, set2, preferred_set1)
                if ret is False:
                    return [False, [], []]
        else:
            return [False, [], []]

        if len(set1) > 0 and len(set2) > 0:
            if not set1 == set2:
                return [True, [list(set1), list(set2)]]
        return [False, [], []]

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
        count_tot = 0
        count_neg = 0
        for i in range(len(conn_components)):
            conn1 = conn_components[i]
            for j in range(i + 1, len(conn_components)):
                conn2 = conn_components[j]
                for act1 in conn1:
                    for act2 in conn2:
                        count_tot = count_tot + 1
                        if not ((act1 in self.outgoing and act2 in self.outgoing[act1]) and (
                                act1 in self.ingoing and act2 in self.ingoing[act1])):
                            count_neg = count_neg + 1

        if count_neg <= shared_constants.PAR_CUT_CONSTANT * count_tot:
            return True

        return False

    def detect_concurrent_cut(self, conn_components, this_nx_graph, strongly_connected_components):
        """
        Detects concurrent cut

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
        conn_components = get_connected_components(self.negated_ingoing, self.negated_outgoing, self.activities,
                                                   force_insert_missing_acti=False)

        if len(conn_components) > 1:
            if self.check_par_cut(conn_components, this_nx_graph, strongly_connected_components):
                return [True, conn_components]

        return [False, []]

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

        if len(self.activities_dir_list) > 1:
            set1 = set()
            set2 = set()

            lc2 = shared_constants.LOOP_CONST_2

            if self.activities_dir_list[0][1] > shared_constants.LOOP_CONST_1:
                if self.activities_dir_list[0][0] in self.ingoing:
                    activ_input = list(self.ingoing[self.activities_dir_list[0][0]])
                    for act in activ_input:
                        if not act == self.activities_dir_list[0][0] and self.activities_direction[act] < lc2:
                            set2.add(act)

            # the constant LOOP_CONST_4 has been revised; moreover it is checked if the 'in-strength' of the exit
            # activity is greater than the 'out-strength' of the any activity in the graph
            if self.activities_dir_list[-1][1] < shared_constants.LOOP_CONST_4 and abs(
                    self.activities_dir_list[-1][1]) > abs(self.activities_dir_list[0][1]):
                set2.add(self.activities_dir_list[-1][0])

            if len(set2) > 0:
                for act in self.activities:
                    if act not in set2 or act in set1:
                        if self.activities_direction[act] < shared_constants.LOOP_CONST_3:
                            set2.add(act)
                        else:
                            set1.add(act)
                if len(set1) > 0:
                    if not set1 == set2:
                        return [True, [set1, set2], True]

        return [False, [], []]

    def __str__(self):
        return "subtree rec_depth="+str(self.rec_depth)+" dfg="+str(self.dfg)+" activities="+str(self.activities)

    def __repr__(self):
        return "subtree rec_depth="+str(self.rec_depth)+" dfg="+str(self.dfg)+" activities="+str(self.activities)

    def detect_cut(self, second_iteration=False):
        """
        Detect generally a cut in the graph (applying all the algorithms)
        """
        if self.dfg:
            # print("\n\n")
            conn_components = get_connected_components(self.ingoing, self.outgoing, self.activities)
            this_nx_graph = None
            strongly_connected_components = None

            conc_cut = self.detect_concurrent_cut(conn_components, this_nx_graph, strongly_connected_components)
            seq_cut = self.detect_sequential_cut(conn_components, this_nx_graph, strongly_connected_components)
            par_cut = self.detect_parallel_cut(conn_components, this_nx_graph, strongly_connected_components)
            loop_cut = self.detect_loop_cut(conn_components, this_nx_graph, strongly_connected_components)

            if conc_cut[0]:
                for comp in conc_cut[1]:
                    new_dfg = filter_dfg_on_act(self.dfg, comp)
                    self.detected_cut = "concurrent"
                    self.children.append(
                        Subtree(new_dfg, self.master_dfg, self.initial_dfg, comp, self.counts, self.rec_depth + 1,
                                noise_threshold=self.noise_threshold,
                                initial_start_activities=self.initial_start_activities,
                                initial_end_activities=self.initial_end_activities))
            else:
                if seq_cut[0]:
                    self.detected_cut = "sequential"
                    for child in seq_cut[1]:
                        dfg_child = filter_dfg_on_act(self.dfg, child)
                        self.children.append(
                            Subtree(dfg_child, self.master_dfg, self.initial_dfg, child, self.counts,
                                    self.rec_depth + 1,
                                    noise_threshold=self.noise_threshold,
                                    initial_start_activities=self.initial_start_activities,
                                    initial_end_activities=self.initial_end_activities))
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
                                Subtree(new_dfg, self.master_dfg, new_dfg, comp, self.counts,
                                        self.rec_depth + 1,
                                        noise_threshold=self.noise_threshold,
                                        initial_start_activities=self.initial_start_activities,
                                        initial_end_activities=self.initial_end_activities))
                    else:
                        if loop_cut[0]:
                            self.detected_cut = "loopCut"
                            for child in loop_cut[1]:
                                dfg_child = filter_dfg_on_act(self.dfg, child)
                                self.children.append(
                                    Subtree(dfg_child, self.master_dfg, self.initial_dfg, child, self.counts,
                                            self.rec_depth + 1,
                                            noise_threshold=self.noise_threshold,
                                            initial_start_activities=self.initial_start_activities,
                                            initial_end_activities=self.initial_end_activities))
                        else:
                            if self.noise_threshold > 0:
                                if not second_iteration:
                                    self.initialize_tree(self.dfg, self.initial_dfg, None, second_iteration=True)
                            else:
                                pass
                            self.detected_cut = "flower"
        else:
            self.detected_cut = "base_concurrent"

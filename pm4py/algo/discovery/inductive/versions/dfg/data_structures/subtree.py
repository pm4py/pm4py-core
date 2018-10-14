from copy import copy
from pm4py.algo.discovery.dfg.utils.dfg_utils import get_ingoing_edges, get_outgoing_edges, get_activities_from_dfg
from pm4py.algo.filtering.dfg.dfg_filtering import clean_dfg_based_on_noise_thresh
from pm4py.algo.discovery.inductive.util import shared_constants
from pm4py.algo.discovery.dfg.utils.dfg_utils import filter_dfg_on_act, negate, get_activities_dirlist, \
    get_activities_self_loop, get_activities_direction


class Subtree(object):
    def __init__(self, dfg, initial_dfg, activities, counts, rec_depth, noise_threshold=0):
        """
        Constructor

        Parameters
        -----------
        dfg
            Directly follows graph of this subtree
        initial_dfg
            Referral directly follows graph that should be taken in account adding hidden/loop transitions
        activities
            Activities of this subtree
        counts
            Shared variable
        rec_depth
            Current recursion depth
        """

        self.initial_dfg = copy(initial_dfg)
        self.counts = counts
        self.rec_depth = rec_depth
        self.noise_threshold = noise_threshold

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

    def determine_best_set_sequential(self, act, set1, set2):
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
            set2.add(act[0])

        return [True, set1, set2]

    def detect_sequential_cut(self, dfg):
        """
        Detect sequential cut in DFG graph
        """
        set1 = set()
        set2 = set()

        if len(self.activities_dir_list) > 0:
            set1.add(self.activities_dir_list[0][0])
        if len(self.activities_dir_list) > -1:
            if not (self.activities_dir_list[0][0] in self.ingoing and self.activities_dir_list[-1][0] in self.ingoing[
                self.activities_dir_list[0][0]]):
                set2.add(self.activities_dir_list[-1][0])
            else:
                return [False, [], []]
        i = 1
        for i in range(1, len(self.activities_dir_list) - 1):
            act = self.activities_dir_list[i]
            ret, set1, set2 = self.determine_best_set_sequential(act, set1, set2)
            if ret is False:
                return [False, [], []]
            i = i + 1

        if len(set1) > 0 and len(set2) > 0:
            if not set1 == set2:
                return [True, list(set1), list(set2)]
        return [False, [], []]

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

            if not ingoing_act in connected_components:
                connected_components.append(ingoing_act)
                activities_considered = activities_considered.union(set(ingoing_act))

        for act in outgoing:
            if not act in ingoing:
                outgoing_act = set(outgoing[act].keys())
                outgoing_act.add(act)
                if not outgoing_act in connected_components:
                    connected_components.append(outgoing_act)
                activities_considered = activities_considered.union(set(outgoing_act))

        max_it = len(connected_components)
        for it in range(max_it-1):
            something_changed = False

            old_connected_components = copy(connected_components)
            connected_components = 0
            connected_components = []

            for i in range(len(old_connected_components)):
                conn1 = old_connected_components[i]

                if conn1 is not None:
                    for j in range(i+1, len(old_connected_components)):
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

        if len(connected_components) == 0:
            for activity in activities:
                connected_components.append([activity])

        return connected_components

    def check_par_cut(self, conn_components):
        """
        Checks if in a parallel cut all relations are present

        Parameters
        -----------
        conn_components
            Connected components
        """
        for i in range(len(conn_components)):
            conn1 = conn_components[i]
            for j in range(i+1, len(conn_components)):
                conn2 = conn_components[j]
                for act1 in conn1:
                    for act2 in conn2:
                        if not ((act1 in self.outgoing and act2 in self.outgoing[act1]) and (
                                act1 in self.ingoing and act2 in self.ingoing[act1])):
                            return False
        return True

    def detect_concurrent_cut(self):
        """
        Detects concurrent cut
        """
        if len(self.dfg) > 0:
            conn_components = self.get_connected_components(self.ingoing, self.outgoing, self.activities)

            if len(conn_components) > 1:
                return [True, conn_components]

        return [False, []]

    def detect_parallel_cut(self):
        """
        Detects parallel cut
        """
        conn_components = self.get_connected_components(self.negated_ingoing, self.negated_outgoing, self.activities)

        if len(conn_components) > 1:
            if self.check_par_cut(conn_components):
                return [True, conn_components]

        return [False, []]

    def detect_loop_cut(self, dfg):
        """
        Detect loop cut
        """

        if len(self.activities_dir_list) > 1:
            set1 = set()
            set2 = set()

            if self.activities_dir_list[0][1] > shared_constants.LOOP_CONST_1:
                if self.activities_dir_list[0][0] in self.ingoing:
                    activ_input = list(self.ingoing[self.activities_dir_list[0][0]])
                    for act in activ_input:
                        if not act == self.activities_dir_list[0][0] and self.activities_direction[
                            act] < shared_constants.LOOP_CONST_2:
                            set2.add(act)

            if self.activities_dir_list[-1][1] < shared_constants.LOOP_CONST_4:
                set2.add(self.activities_dir_list[-1][0])

            if len(set2) > 0:
                for act in self.activities:
                    if not act in set2 or act in set1:
                        if self.activities_direction[act] < shared_constants.LOOP_CONST_3:
                            set2.add(act)
                        else:
                            set1.add(act)
                if len(set1) > 0:
                    if not set1 == set2:
                        return [True, set1, set2]

        return [False, [], []]

    def add_to_most_probable_component(self, comps, act2, ingoing, outgoing):
        """
        Adds a lost component in parallel cut detection to the most probable component

        Parameters
        -------------
        comps
            Connected components
        act2
            Activity that has been missed
        ingoing
            Map of ingoing attributes
        outgoing
            Map of outgoing attributes

        Returns
        -------------
        comps
            Fixed connected components
        """
        sums = []
        idx_max_sum = 0

        for comp in comps:
            summ = 0
            for act1 in comp:
                if act1 in ingoing and act2 in ingoing[act1]:
                    summ = summ + ingoing[act1][act2]
                if act1 in outgoing and act2 in outgoing[act1]:
                    summ = summ + outgoing[act1][act2]
            sums.append(summ)
            if sums[-1] > sums[idx_max_sum]:
                idx_max_sum = len(sums) - 1

        comps[idx_max_sum].add(act2)

        return comps

    def detect_cut(self, second_iteration=False):
        """
        Detect generally a cut in the graph (applying all the algorithms)
        """
        if self.dfg:
            par_cut = self.detect_parallel_cut()
            conc_cut = self.detect_concurrent_cut()
            seq_cut = self.detect_sequential_cut(self.dfg)
            loop_cut = self.detect_loop_cut(self.dfg)

            if par_cut[0]:
                union_acti_comp = set()
                for comp in par_cut[1]:
                    union_acti_comp = union_acti_comp.union(comp)
                diff_acti_comp = set(self.activities).difference(union_acti_comp)

                for act in diff_acti_comp:
                    par_cut[1] = self.add_to_most_probable_component(par_cut[1], act, self.ingoing, self.outgoing)

                for comp in par_cut[1]:
                    new_dfg = filter_dfg_on_act(self.dfg, comp)
                    self.detected_cut = "parallel"
                    self.children.append(Subtree(new_dfg, self.initial_dfg, comp, self.counts, self.rec_depth + 1,
                                                 noise_threshold=self.noise_threshold))
            else:
                if conc_cut[0]:
                    for comp in conc_cut[1]:
                        new_dfg = filter_dfg_on_act(self.dfg, comp)
                        self.detected_cut = "concurrent"
                        self.children.append(Subtree(new_dfg, self.initial_dfg, comp, self.counts, self.rec_depth + 1,
                                                     noise_threshold=self.noise_threshold))
                else:
                    if seq_cut[0]:
                        dfg1 = filter_dfg_on_act(self.dfg, seq_cut[1])
                        dfg2 = filter_dfg_on_act(self.dfg, seq_cut[2])
                        self.detected_cut = "sequential"
                        self.children.append(Subtree(dfg1, self.initial_dfg, seq_cut[1], self.counts, self.rec_depth + 1,
                                                     noise_threshold=self.noise_threshold))
                        self.children.append(Subtree(dfg2, self.initial_dfg, seq_cut[2], self.counts, self.rec_depth + 1,
                                                     noise_threshold=self.noise_threshold))
                    else:
                        if loop_cut[0]:
                            dfg1 = filter_dfg_on_act(self.dfg, loop_cut[1])
                            dfg2 = filter_dfg_on_act(self.dfg, loop_cut[2])
                            self.detected_cut = "loopCut"
                            self.children.append(
                                Subtree(dfg1, self.initial_dfg, loop_cut[1], self.counts, self.rec_depth + 1,
                                        noise_threshold=self.noise_threshold))
                            self.children.append(
                                Subtree(dfg2, self.initial_dfg, loop_cut[2], self.counts, self.rec_depth + 1,
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

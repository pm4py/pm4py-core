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
import numpy as np, pkgutil, logging

from copy import copy

from pm4py.objects.dfg.utils.dfg_utils import get_all_activities_connected_as_input_to_activity
from pm4py.objects.dfg.utils.dfg_utils import get_all_activities_connected_as_output_to_activity
from pm4py.objects.dfg.utils.dfg_utils import filter_dfg_on_act, negate, get_activities_dirlist, \
    get_activities_self_loop, get_activities_direction
from pm4py.objects.dfg.utils.dfg_utils import get_ingoing_edges, get_outgoing_edges, get_activities_from_dfg, \
    infer_start_activities, infer_end_activities
from pm4py.algo.filtering.dfg.dfg_filtering import clean_dfg_based_on_noise_thresh
from pm4py.objects.dfg.utils.dfg_utils import infer_start_activities_from_prev_connections_and_current_dfg, \
    infer_end_activities_from_succ_connections_and_current_dfg, transform_dfg_to_directed_nx_graph
from pm4py.algo.discovery.inductive.util import parallel_cut_utils, detection_utils


class SubtreeDFGBased():
    def __init__(self, dfg, master_dfg, initial_dfg, activities, counts, rec_depth, noise_threshold=0,
                 initial_start_activities=None, initial_end_activities=None):
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
        noise_threshold
            Noise threshold
        initial_start_activities
            Start activities of the log
        initial_end_activities
            End activities of the log
        """
        self.master_dfg = copy(master_dfg)
        self.initial_dfg = copy(initial_dfg)
        self.counts = counts
        self.rec_depth = rec_depth
        self.noise_threshold = noise_threshold
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

        # start/end activities of the initial log intersected with the current set of activities
        self.initial_start_activities = list(set(self.initial_start_activities).intersection(set(self.activities)))
        self.initial_end_activities = list(set(self.initial_end_activities).intersection(set(self.activities)))

        if rec_depth > 0:
            self.start_activities = list(
                set(self.initial_start_activities).union(infer_start_activities(self.dfg)).union(
                    infer_start_activities_from_prev_connections_and_current_dfg(self.initial_dfg, self.dfg,
                                                                                 self.activities)).intersection(
                    self.activities))
            self.end_activities = list(set(self.initial_end_activities).union(infer_end_activities(self.dfg)).union(
                infer_end_activities_from_succ_connections_and_current_dfg(self.initial_dfg, self.dfg,
                                                                           self.activities)).intersection(
                self.activities))
        else:
            self.start_activities = self.initial_start_activities
            self.end_activities = self.initial_end_activities

        self.detect_cut()

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

        if second_iteration:
            self.detect_cut(second_iteration=second_iteration)

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
        all_start_activities = self.start_activities
        all_end_activities = self.end_activities

        start_activities = all_start_activities
        end_activities = list(set(all_end_activities) - set(all_start_activities))
        start_act_that_are_also_end = list(set(all_end_activities) - set(end_activities))

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
                return [True, [do_part + exit_part, redo_part], True, len(start_act_that_are_also_end) > 0]
            else:
                return [True, [do_part, redo_part + exit_part], False, len(start_act_that_are_also_end) > 0]

        return [False, [], False]

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
            conn_matrix = detection_utils.get_connection_matrix(strongly_connected_components, self.dfg)
            comps = []
            closed = set()
            for i in range(conn_matrix.shape[0]):
                if max(conn_matrix[i, :]) == 0:
                    if len(comps) == 0:
                        comps.append([])
                    comps[-1].append(i)
                    closed.add(i)
            cyc_continue = len(comps) >= 1
            while cyc_continue:
                cyc_continue = False
                curr_comp = []
                for i in range(conn_matrix.shape[0]):
                    if i not in closed:
                        i_j = set()
                        for j in range(conn_matrix.shape[1]):
                            if conn_matrix[i][j] == 1.0:
                                i_j.add(j)
                        i_j_minus = i_j.difference(closed)
                        if len(i_j_minus) == 0:
                            curr_comp.append(i)
                            closed.add(i)
                if curr_comp:
                    cyc_continue = True
                    comps.append(curr_comp)
            last_cond = False
            for i in range(conn_matrix.shape[0]):
                if i not in closed:
                    if not last_cond:
                        last_cond = True
                        comps.append([])
                    comps[-1].append(i)
            if len(comps) > 1:
                comps = [detection_utils.perform_list_union(list(set(strongly_connected_components[i]) for i in comp))
                         for comp in
                         comps]
                return [True, comps]
        return [False, [], []]

    def check_sa_ea_for_each_branch(self, conn_components):
        """
        Checks if each branch of the parallel cut has a start
        and an end node of the subgraph

        Parameters
        --------------
        conn_components
            Parallel cut

        Returns
        -------------
        boolean
            True if each branch of the parallel cut has a start and an end node
        """
        parallel_cut_sa = list(set(self.initial_start_activities).union(
            infer_start_activities_from_prev_connections_and_current_dfg(self.initial_dfg, self.dfg, self.activities,
                                                                         include_self=False)).intersection(
            self.activities))
        parallel_cut_ea = list(set(self.initial_end_activities).union(
            infer_end_activities_from_succ_connections_and_current_dfg(self.initial_dfg, self.dfg, self.activities,
                                                                       include_self=False)).intersection(
            self.activities))

        if conn_components is None:
            return False

        for comp in conn_components:
            comp_sa_ok = False
            comp_ea_ok = False

            for sa in parallel_cut_sa:
                if sa in comp:
                    comp_sa_ok = True
                    break
            for ea in parallel_cut_ea:
                if ea in comp:
                    comp_ea_ok = True
                    break

            if not (comp_sa_ok and comp_ea_ok):
                return False

        return True

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
        conn_components = detection_utils.get_connected_components(self.negated_ingoing, self.negated_outgoing,
                                                                   self.activities)

        if len(conn_components) > 1:
            conn_components = parallel_cut_utils.check_par_cut(conn_components, self.ingoing, self.outgoing)

            if self.check_sa_ea_for_each_branch(conn_components):
                return [True, conn_components]

        return [False, []]

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
                if act in self.outgoing:
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
        remaining_act = self.start_activities
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

    def detect_cut(self, second_iteration=False):
        """
        Detect generally a cut in the graph (applying all the algorithms)
        """
        if pkgutil.find_loader("networkx"):
            import networkx as nx
        else:
            msg = "networkx is not available. inductive miner cannot be used!"
            logging.error(msg)
            raise Exception(msg)

        if self.dfg:

            this_nx_graph = transform_dfg_to_directed_nx_graph(self.dfg, activities=self.activities)
            conn_components = detection_utils.get_connected_components(self.ingoing, self.outgoing, self.activities)
            strongly_connected_components = [list(x) for x in nx.strongly_connected_components(this_nx_graph)]

            xor_cut = self.detect_xor_cut(conn_components, this_nx_graph, strongly_connected_components)

            if xor_cut[0]:
                for comp in xor_cut[1]:
                    new_dfg = filter_dfg_on_act(self.dfg, comp)
                    self.detected_cut = "xor"
                    self.children.append(
                        SubtreeDFGBased(new_dfg, self.master_dfg, self.initial_dfg, comp, self.counts,
                                        self.rec_depth + 1,
                                        noise_threshold=self.noise_threshold,
                                        initial_start_activities=self.initial_start_activities,
                                        initial_end_activities=self.initial_end_activities))
            else:
                seq_cut = self.detect_sequential_cut(conn_components, this_nx_graph, strongly_connected_components)
                if seq_cut[0]:
                    self.detected_cut = "sequential"
                    for child in seq_cut[1]:
                        dfg_child = filter_dfg_on_act(self.dfg, child)
                        self.children.append(
                            SubtreeDFGBased(dfg_child, self.master_dfg, self.initial_dfg, child, self.counts,
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
                                SubtreeDFGBased(new_dfg, self.master_dfg, new_dfg, comp, self.counts,
                                                self.rec_depth + 1,
                                                noise_threshold=self.noise_threshold,
                                                initial_start_activities=self.initial_start_activities,
                                                initial_end_activities=self.initial_end_activities))
                    else:
                        loop_cut = self.detect_loop_cut(conn_components, this_nx_graph, strongly_connected_components)
                        if loop_cut[0]:
                            if loop_cut[2]:
                                self.detected_cut = "loopCut"
                                for index_enum, child in enumerate(loop_cut[1]):
                                    dfg_child = filter_dfg_on_act(self.dfg, child)
                                    next_subtree = SubtreeDFGBased(dfg_child, self.master_dfg, self.initial_dfg, child,
                                                                   self.counts, self.rec_depth + 1,
                                                                   noise_threshold=self.noise_threshold,
                                                                   initial_start_activities=self.initial_start_activities,
                                                                   initial_end_activities=self.initial_end_activities)
                                    if loop_cut[3]:
                                        next_subtree.must_insert_skip = True
                                    self.children.append(next_subtree)
                            else:
                                self.detected_cut = "sequential"
                                self.need_loop_on_subtree = True
                                for index_enum, child in enumerate(loop_cut[1]):
                                    dfg_child = filter_dfg_on_act(self.dfg, child)
                                    next_subtree = SubtreeDFGBased(dfg_child, self.master_dfg, self.initial_dfg, child,
                                                                   self.counts, self.rec_depth + 1,
                                                                   noise_threshold=self.noise_threshold,
                                                                   initial_start_activities=self.initial_start_activities,
                                                                   initial_end_activities=self.initial_end_activities)
                                    self.children.append(next_subtree)
                                    next_subtree.must_insert_skip = True
                        else:
                            if self.noise_threshold > 0:
                                if not second_iteration:
                                    self.initialize_tree(self.dfg, self.initial_dfg, None, second_iteration=True)
                                else:
                                    self.detected_cut = "flower"
                            else:
                                self.detected_cut = "flower"

        else:
            self.detected_cut = "base_xor"

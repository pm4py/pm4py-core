from copy import copy
import pkgutil

from pm4py.algo.discovery.dfg.utils.dfg_utils import get_activities_from_dfg, \
    infer_start_activities, infer_end_activities
from pm4py.algo.discovery.dfg.utils.dfg_utils import get_ingoing_edges, get_outgoing_edges
from pm4py.algo.discovery.dfg.utils.dfg_utils import negate, get_activities_self_loop, transform_dfg_to_directed_nx_graph
from pm4py.algo.discovery.dfg.versions import native as dfg_inst
from pm4py.algo.filtering.dfg.dfg_filtering import clean_dfg_based_on_noise_thresh
from pm4py.algo.discovery.inductive.versions.im.util import base_case, fall_through
from pm4py import util as pmutil
from pm4py.algo.discovery.inductive.versions.im.util import splitting as split
from pm4py.algo.discovery.inductive.util import parallel_cut_utils, detection_utils, cut_detection
from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.algo.filtering.log.end_activities import end_activities_filter
from pm4py.algo.filtering.log.start_activities import start_activities_filter
from pm4py.algo.discovery.inductive.versions.im.util import constants as inductive_consts
from pm4py.algo.discovery.inductive.parameters import Parameters
from pm4py.util import exec_utils
from pm4py.objects.log.util import filtering_utils
import logging


class SubtreePlain(object):
    def __init__(self, log, dfg, master_dfg, initial_dfg, activities, counts, rec_depth, noise_threshold=0,
                 start_activities=None, end_activities=None, initial_start_activities=None,
                 initial_end_activities=None, parameters=None, real_init=True):
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
        if real_init:
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
            self.log = log
            self.inverted_dfg = None
            self.original_log = log

            self.initialize_tree(dfg, log, initial_dfg, activities, parameters=parameters)

    def __deepcopy__(self, memodict={}):
        """
            def __init__(self, log, dfg, master_dfg, initial_dfg, activities, counts, rec_depth, noise_threshold=0,
                 start_activities=None, end_activities=None, initial_start_activities=None,
                 initial_end_activities=None, parameters=None, real_init=False):
        :param memodict:
        :return:
        """
        S = SubtreePlain(None, None, None, None, None, None, None, real_init=False)
        S.master_dfg = self.master_dfg
        S.initial_dfg = self.initial_dfg
        S.counts = self.counts
        S.rec_depth = self.rec_depth
        S.noise_threshold = self.noise_threshold
        S.start_activities = self.start_activities
        S.end_activities = self.end_activities
        S.initial_start_activities = self.initial_start_activities
        S.initial_end_activities = self.initial_end_activities
        S.second_iteration = self.second_iteration
        S.activities = self.activities
        S.dfg = self.dfg
        S.outgoing = self.outgoing
        S.ingoing = self.ingoing
        S.self_loop_activities = self.self_loop_activities
        S.initial_ingoing = self.initial_ingoing
        S.initial_outgoing = self.initial_outgoing
        S.activities_direction = self.activities_direction
        S.activities_dir_list = self.activities_dir_list
        S.negated_dfg = self.negated_dfg
        S.negated_activities = self.negated_activities
        S.negated_outgoing = self.negated_outgoing
        S.negated_ingoing = self.negated_ingoing
        S.detected_cut = self.detected_cut
        S.children = self.children
        S.must_insert_skip = self.must_insert_skip
        S.log = self.log
        S.inverted_dfg = self.inverted_dfg
        S.original_log = self.original_log
        try:
            S.parameters = self.parameters
        except:
            pass
        return S

    def initialize_tree(self, dfg, log, initial_dfg, activities, second_iteration=False, end_call=True,
                        parameters=None):
        """
            Initialize the tree


            Parameters
            -----------
            dfg
                Directly follows graph of this subtree
            log
                the event log
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
        self.negated_dfg = negate(self.dfg)
        self.negated_activities = get_activities_from_dfg(self.negated_dfg)
        self.negated_outgoing = get_outgoing_edges(self.negated_dfg)
        self.negated_ingoing = get_ingoing_edges(self.negated_dfg)
        self.detected_cut = None
        self.children = []
        self.log = log
        self.original_log = log
        self.parameters = parameters

        self.detect_cut(second_iteration=False, parameters=parameters)

    def create_dfg(self, parameters=None):
        if parameters is None:
            parameters = {}

        dfg = [(k, v) for k, v in dfg_inst.apply(self.log, parameters=parameters).items() if v > 0]

        return dfg

    def is_followed_by(self, dfg, activity_a, activity_b):
        """
        check if Activity A is followed by Activity B in the dfg of self, returns bool.
        """
        for i in range(0, len(dfg)):
            if (activity_a, activity_b) == dfg[i][0]:
                return True

        return False

    def detect_xor(self, conn_components):
        """
        Detects xor cut
        Parameters
        --------------
        conn_components
            Connected components
        this_nx_graph
            NX graph calculated on the DFG
        strongly_connected_components
            Strongly connected components
        """
        if not self.contains_empty_trace() and len(conn_components) > 1:
            return [True, conn_components]

        return [False, []]

    def detect_concurrent(self):
        if self.contains_empty_trace():
            return [False, []]
        inverted_dfg = []  # create an inverted dfg, the connected components of this dfg are the split
        for a in self.activities:
            for b in self.activities:
                if a != b:
                    if not self.is_followed_by(self.dfg, a, b) or not self.is_followed_by(self.dfg, b, a):
                        if ((a, b), 1) not in inverted_dfg:
                            inverted_dfg.append(((a, b), 1))
                            inverted_dfg.append(((b, a), 1))
        self.inverted_dfg = inverted_dfg
        new_ingoing = get_ingoing_edges(inverted_dfg)
        new_outgoing = get_outgoing_edges(inverted_dfg)
        conn = detection_utils.get_connected_components(new_ingoing, new_outgoing, self.activities)
        if len(conn) > 1:
            conn = parallel_cut_utils.check_par_cut(conn, self.ingoing, self.outgoing)
            if len(conn) > 1:
                if parallel_cut_utils.check_sa_ea_for_each_branch(conn, self.start_activities, self.end_activities):
                    return [True, conn]

        return [False, []]

    def get_index_of_x_in_list(self, x, li):
        for i in range(0, len(li)):
            if li[i] == x:
                return i

    def find_set_with_x(self, x, list_of_sets):
        for i in range(0, len(list_of_sets)):
            if x in list_of_sets[i]:
                return i

    def contains_empty_trace(self):
        contains = False
        for trace in self.log:
            if len(trace) == 0:
                contains = True
        return contains

    def detect_loop(self):
        # p0 is part of return value, it contains the partition of activities
        # write all start and end activities in p1
        if self.contains_empty_trace():
            return [False, []]
        p1 = []
        for act in self.start_activities:
            if act not in p1:
                p1.append(act)
        for act in self.end_activities:
            if act not in p1:
                p1.append(act)

        # create new dfg without the transitions to start and end activities
        new_dfg = copy(self.dfg)
        copy_dfg = copy(new_dfg)
        for ele in copy_dfg:
            if ele[0][0] in p1 or ele[0][1] in p1:
                new_dfg.remove(ele)

        current_activities = {}
        iterate_order = []
        for element in self.activities:
            if element not in p1:
                current_activities.update({element: 1})
                iterate_order.append(element)
        # create an overview of what activity has which outgoing connections
        outgoing = [list() for _ in range(len(iterate_order))]
        for i in range(0, len(iterate_order)):
            current_act = iterate_order[i]
            for element in new_dfg:
                if element[0][0] == current_act:
                    if element[0][1] in iterate_order:
                        outgoing[i].append(element[0][1])

        # built p2, ..., pn :
        acts_not_assigned_to_set = copy(iterate_order)
        p = [list() for _ in range(len(iterate_order))]
        max_set = iterate_order
        max_set_found = False
        for i in range(0, len(iterate_order)):
            act = iterate_order[i]
            if act in acts_not_assigned_to_set:
                p[i] = [act]
                acts_not_assigned_to_set.remove(act)
                added = True
                while added:
                    added = False
                    # check if max set is already found
                    count = 0
                    for li in p:
                        if len(li) != 0:
                            count += 1
                    if count == len(max_set):
                        max_set_found = True
                        break
                    # if max set is not found, continue adding acts
                    for act_b in p[i]:
                        index_of_act_b_in_outgoing = self.get_index_of_x_in_list(act_b, iterate_order)
                        for outgoing_act in outgoing[index_of_act_b_in_outgoing]:
                            if outgoing_act in acts_not_assigned_to_set:
                                acts_not_assigned_to_set.remove(outgoing_act)
                                p[i].append(outgoing_act)
                                added = True
                                break
                        if added:
                            break
            if max_set_found:
                break

        for li in p:
            if len(li) == 0:
                p.remove(li)

        # p0 = get_connected_components(new_ingoing, new_outgoing, current_activities)
        p.insert(0, p1)
        p0 = p
        iterable_dfg = []
        for i in range(0, len(self.dfg)):
            iterable_dfg.append(self.dfg[i][0])
        # p0 is like P1,P2,...,Pn in line 3 on page 190 of the IM Thesis
        # check for subsets in p0 that have connections to and end or from a start activity
        p0_copy = []
        for int_el in p0:
            p0_copy.append(int_el)
        for element in p0_copy:  # for every set in p0
            removed = False
            if element in p0 and element != p0[0]:
                for act in element:  # for every activity in this set
                    for e in self.end_activities:  # for every end activity
                        if e not in self.start_activities:
                            if (act, e) in iterable_dfg:  # check if connected
                                # is there an element in dfg pointing from any act in a subset of p0 to an end activity
                                for activ in element:
                                    if activ not in p0[0]:
                                        p0[0].append(activ)
                                if element in p0:
                                    p0.remove(element)  # remove subsets that are connected to an end activity
                                removed = True
                                break
                    if removed:
                        break
                    for s in self.start_activities:
                        if s not in self.end_activities:
                            if not removed:
                                if (s, act) in iterable_dfg:
                                    for acti in element:
                                        if acti not in p0[0]:
                                            p0[0].append(acti)
                                    if element in p0:
                                        p0.remove(element)  # remove subsets that are connected to an end activity
                                    removed = True
                                    break
                            else:
                                break
                    if removed:
                        break

        iterable_dfg = list()
        for i in range(0, len(self.dfg)):
            iterable_dfg.append(self.dfg[i][0])

        p0_copy = []
        for int_el in p0:
            p0_copy.append(int_el)
        for element in p0:
            if element in p0 and element != p0[0]:
                for act in element:
                    for e in self.end_activities:
                        if (e, act) in iterable_dfg:  # get those act, that are connected from an end activity
                            for e2 in self.end_activities:  # check, if the act is connected from all end activities
                                if (e2, act) not in iterable_dfg:
                                    for acti in element:
                                        if acti not in p0[0]:
                                            p0[0].append(acti)
                                    if element in p0:
                                        p0.remove(element)  # remove subsets that are connected to an end activity
                                    break
                    for s in self.start_activities:
                        if (act, s) in iterable_dfg:  # same as above (in this case for activities connected to
                            # a start activity)
                            for s2 in self.start_activities:
                                if (act, s2) not in iterable_dfg:
                                    for acti in element:
                                        if acti not in p0[0]:
                                            p0[0].append(acti)
                                    if element in p0:
                                        p0.remove(element)  # remove subsets that are connected to an end activity
                                    break
        index_to_delete = []
        for i in range(0, len(p0)):
            if not p0[i]:
                index_to_delete.insert(0, i)
        for index in index_to_delete:
            p0.remove(p0[index])
        if len(p0) > 1:
            return [True, p0]
        else:
            return [False, []]

    def check_for_cut(self, test_log, deleted_activity=None, parameters=None):
        if pkgutil.find_loader("networkx"):
            import networkx as nx

            if deleted_activity is not None:
                del self.activities[deleted_activity]
            if parameters is None:
                parameters = {}
            dfg = [(k, v) for k, v in dfg_inst.apply(test_log, parameters=parameters).items() if v > 0]
            self.dfg = dfg
            self.outgoing = get_outgoing_edges(self.dfg)
            self.ingoing = get_ingoing_edges(self.dfg)
            self.log = test_log
            conn_components = detection_utils.get_connected_components(self.ingoing, self.outgoing, self.activities)
            this_nx_graph = transform_dfg_to_directed_nx_graph(self.dfg, activities=self.activities)
            strongly_connected_components = [list(x) for x in nx.strongly_connected_components(this_nx_graph)]
            # search for cut and return true as soon as a cut is found:
            xor_cut = self.detect_xor(conn_components)
            if xor_cut[0]:
                return True
            else:
                sequence_cut = cut_detection.detect_sequential_cut(self, self.dfg, strongly_connected_components)
                if sequence_cut[0]:
                    return True
                else:
                    parallel_cut = self.detect_concurrent()
                    if parallel_cut[0]:
                        return True
                    else:
                        loop_cut = self.detect_loop()
                        if loop_cut[0]:
                            return True
                        else:
                            return False
        else:
            msg = "networkx is not available. inductive miner cannot be used!"
            logging.error(msg)
            raise Exception(msg)

    def detect_cut(self, second_iteration=False, parameters=None):
        if pkgutil.find_loader("networkx"):
            import networkx as nx

            if parameters is None:
                parameters = {}
            activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters,
                                                      pmutil.xes_constants.DEFAULT_NAME_KEY)

            # check base cases:
            empty_log = base_case.empty_log(self.log)
            single_activity = base_case.single_activity(self.log, activity_key)
            if empty_log:
                self.detected_cut = 'empty_log'
            elif single_activity:
                self.detected_cut = 'single_activity'
            # if no base cases are found, search for a cut:
            else:
                conn_components = detection_utils.get_connected_components(self.ingoing, self.outgoing, self.activities)
                this_nx_graph = transform_dfg_to_directed_nx_graph(self.dfg, activities=self.activities)
                strongly_connected_components = [list(x) for x in nx.strongly_connected_components(this_nx_graph)]
                xor_cut = self.detect_xor(conn_components)
                # the following part searches for a cut in the current log
                # if a cut is found, the log is split according to the cut, the resulting logs are saved in new_logs
                # recursion is used on all the logs in new_logs
                if xor_cut[0]:
                    logging.debug("xor_cut")
                    self.detected_cut = 'concurrent'
                    new_logs = split.split_xor(xor_cut[1], self.log, activity_key)
                    for i in range(len(new_logs)):
                        new_logs[i] = filtering_utils.keep_one_trace_per_variant(new_logs[i], parameters=parameters)
                    for l in new_logs:
                        new_dfg = [(k, v) for k, v in dfg_inst.apply(l, parameters=parameters).items() if v > 0]
                        activities = attributes_filter.get_attribute_values(l, activity_key)
                        start_activities = list(
                            start_activities_filter.get_start_activities(l, parameters=parameters).keys())
                        end_activities = list(
                            end_activities_filter.get_end_activities(l, parameters=parameters).keys())
                        self.children.append(
                            SubtreePlain(l, new_dfg, self.master_dfg, self.initial_dfg, activities, self.counts,
                                         self.rec_depth + 1,
                                         noise_threshold=self.noise_threshold, start_activities=start_activities,
                                         end_activities=end_activities,
                                         initial_start_activities=self.initial_start_activities,
                                         initial_end_activities=self.initial_end_activities,
                                         parameters=parameters))
                else:
                    sequence_cut = cut_detection.detect_sequential_cut(self, self.dfg, strongly_connected_components)
                    if sequence_cut[0]:
                        logging.debug("sequence_cut")
                        new_logs = split.split_sequence(sequence_cut[1], self.log, activity_key)
                        for i in range(len(new_logs)):
                            new_logs[i] = filtering_utils.keep_one_trace_per_variant(new_logs[i],
                                                                                     parameters=parameters)
                        self.detected_cut = "sequential"
                        for l in new_logs:
                            new_dfg = [(k, v) for k, v in dfg_inst.apply(l, parameters=parameters).items() if v > 0]
                            activities = attributes_filter.get_attribute_values(l, activity_key)
                            start_activities = list(
                                start_activities_filter.get_start_activities(l, parameters=parameters).keys())
                            end_activities = list(
                                end_activities_filter.get_end_activities(l, parameters=parameters).keys())
                            self.children.append(
                                SubtreePlain(l, new_dfg, self.master_dfg, self.initial_dfg, activities, self.counts,
                                             self.rec_depth + 1,
                                             noise_threshold=self.noise_threshold, start_activities=start_activities,
                                             end_activities=end_activities,
                                             initial_start_activities=self.initial_start_activities,
                                             initial_end_activities=self.initial_end_activities,
                                             parameters=parameters))
                    else:
                        parallel_cut = self.detect_concurrent()
                        if parallel_cut[0]:
                            logging.debug("parallel_cut")
                            new_logs = split.split_parallel(parallel_cut[1], self.log, activity_key)
                            for i in range(len(new_logs)):
                                new_logs[i] = filtering_utils.keep_one_trace_per_variant(new_logs[i],
                                                                                         parameters=parameters)
                            self.detected_cut = "parallel"
                            for l in new_logs:
                                new_dfg = [(k, v) for k, v in dfg_inst.apply(l, parameters=parameters).items() if v > 0]
                                activities = attributes_filter.get_attribute_values(l, activity_key)
                                start_activities = list(
                                    start_activities_filter.get_start_activities(l,
                                                                                 parameters=parameters).keys())
                                end_activities = list(
                                    end_activities_filter.get_end_activities(l, parameters=parameters).keys())
                                self.children.append(
                                    SubtreePlain(l, new_dfg, self.master_dfg, self.initial_dfg, activities, self.counts,
                                                 self.rec_depth + 1,
                                                 noise_threshold=self.noise_threshold,
                                                 start_activities=start_activities,
                                                 end_activities=end_activities,
                                                 initial_start_activities=self.initial_start_activities,
                                                 initial_end_activities=self.initial_end_activities,
                                                 parameters=parameters))
                        else:
                            loop_cut = self.detect_loop()
                            if loop_cut[0]:
                                logging.debug("loop_cut")
                                new_logs = split.split_loop(loop_cut[1], self.log, activity_key)
                                for i in range(len(new_logs)):
                                    new_logs[i] = filtering_utils.keep_one_trace_per_variant(new_logs[i],
                                                                                             parameters=parameters)
                                self.detected_cut = "loopCut"
                                for l in new_logs:
                                    new_dfg = [(k, v) for k, v in dfg_inst.apply(l, parameters=parameters).items() if
                                               v > 0]
                                    activities = attributes_filter.get_attribute_values(l, activity_key)
                                    start_activities = list(
                                        start_activities_filter.get_start_activities(l,
                                                                                     parameters=parameters).keys())
                                    end_activities = list(
                                        end_activities_filter.get_end_activities(l,
                                                                                 parameters=parameters).keys())
                                    self.children.append(
                                        SubtreePlain(l, new_dfg, self.master_dfg, self.initial_dfg, activities,
                                                     self.counts,
                                                     self.rec_depth + 1,
                                                     noise_threshold=self.noise_threshold,
                                                     start_activities=start_activities,
                                                     end_activities=end_activities,
                                                     initial_start_activities=self.initial_start_activities,
                                                     initial_end_activities=self.initial_end_activities,
                                                     parameters=parameters))

                            # if the code gets to this point, there is no base_case and no cut found in the log
                            # therefore, we now apply fall through:
                            else:
                                self.apply_fall_through(parameters)
        else:
            msg = "networkx is not available. inductive miner cannot be used!"
            logging.error(msg)
            raise Exception(msg)

    # this is called at the end of detect_cut, if no cut was found and a fallthrough needs to be applied
    def apply_fall_through(self, parameters=None):
        if parameters is None:
            parameters = {}
        activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters,
                                                  pmutil.xes_constants.DEFAULT_NAME_KEY)

        # set flags for fall_throughs, base case is True (enabled)
        use_empty_trace = (Parameters.EMPTY_TRACE_KEY not in parameters) or parameters[
            Parameters.EMPTY_TRACE_KEY]
        use_act_once_per_trace = (Parameters.ONCE_PER_TRACE_KEY not in parameters) or parameters[
            Parameters.ONCE_PER_TRACE_KEY]
        use_act_concurrent = (Parameters.CONCURRENT_KEY not in parameters) or parameters[
            Parameters.CONCURRENT_KEY]
        use_strict_tau_loop = (Parameters.STRICT_TAU_LOOP_KEY not in parameters) or parameters[
            Parameters.STRICT_TAU_LOOP_KEY]
        use_tau_loop = (Parameters.TAU_LOOP_KEY not in parameters) or parameters[Parameters.TAU_LOOP_KEY]

        if use_empty_trace:
            empty_trace, new_log = fall_through.empty_trace(self.log)
            # if an empty trace is found, the empty trace fallthrough applies
            #
        else:
            empty_trace = False
        if empty_trace:
            logging.debug("empty_trace")
            activites_left = []
            for trace in new_log:
                for act in trace:
                    if act[activity_key] not in activites_left:
                        activites_left.append(act[activity_key])
            self.detected_cut = 'empty_trace'
            new_dfg = [(k, v) for k, v in dfg_inst.apply(new_log, parameters=parameters).items() if v > 0]
            activities = attributes_filter.get_attribute_values(new_log, activity_key)
            start_activities = list(
                start_activities_filter.get_start_activities(new_log, parameters=self.parameters).keys())
            end_activities = list(end_activities_filter.get_end_activities(new_log, parameters=self.parameters).keys())
            self.children.append(
                SubtreePlain(new_log, new_dfg, self.master_dfg, self.initial_dfg, activities, self.counts,
                             self.rec_depth + 1,
                             noise_threshold=self.noise_threshold,
                             start_activities=start_activities,
                             end_activities=end_activities,
                             initial_start_activities=self.initial_start_activities,
                             initial_end_activities=self.initial_end_activities,
                             parameters=parameters))
        else:
            if use_act_once_per_trace:
                activity_once, new_log, small_log = fall_through.act_once_per_trace(self.log, self.activities,
                                                                                    activity_key)
                small_log = filtering_utils.keep_one_trace_per_variant(small_log, parameters=parameters)
            else:
                activity_once = False
            if use_act_once_per_trace and activity_once:
                self.detected_cut = 'parallel'
                # create two new dfgs as we need them to append to self.children later
                new_dfg = [(k, v) for k, v in dfg_inst.apply(new_log, parameters=parameters).items() if
                           v > 0]
                activities = attributes_filter.get_attribute_values(new_log, activity_key)
                small_dfg = [(k, v) for k, v in dfg_inst.apply(small_log, parameters=parameters).items() if
                             v > 0]
                small_activities = attributes_filter.get_attribute_values(small_log, activity_key)
                self.children.append(
                    SubtreePlain(small_log, small_dfg, self.master_dfg, self.initial_dfg, small_activities,
                                 self.counts,
                                 self.rec_depth + 1,
                                 noise_threshold=self.noise_threshold,
                                 initial_start_activities=self.initial_start_activities,
                                 initial_end_activities=self.initial_end_activities,
                                 parameters=parameters))
                # continue with the recursion on the new log
                start_activities = list(
                    start_activities_filter.get_start_activities(new_log, parameters=self.parameters).keys())
                end_activities = list(
                    end_activities_filter.get_end_activities(new_log, parameters=self.parameters).keys())
                self.children.append(
                    SubtreePlain(new_log, new_dfg, self.master_dfg, self.initial_dfg, activities,
                                 self.counts,
                                 self.rec_depth + 1,
                                 noise_threshold=self.noise_threshold,
                                 start_activities=start_activities,
                                 end_activities=end_activities,
                                 initial_start_activities=self.initial_start_activities,
                                 initial_end_activities=self.initial_end_activities,
                                 parameters=parameters))

            else:
                if use_act_concurrent:
                    activity_concurrent, new_log, small_log, activity_left_out = fall_through.activity_concurrent(self,
                                                                                                                  self.log,
                                                                                                                  self.activities,
                                                                                                                  activity_key,
                                                                                                                  parameters=parameters)
                    small_log = filtering_utils.keep_one_trace_per_variant(small_log, parameters=parameters)
                else:
                    activity_concurrent = False
                if use_act_concurrent and activity_concurrent:
                    self.detected_cut = 'parallel'
                    # create two new dfgs on to append later
                    new_dfg = [(k, v) for k, v in dfg_inst.apply(new_log, parameters=parameters).items() if
                               v > 0]
                    activities = attributes_filter.get_attribute_values(new_log, activity_key)
                    small_dfg = [(k, v) for k, v in dfg_inst.apply(small_log, parameters=parameters).items() if
                                 v > 0]
                    small_activities = attributes_filter.get_attribute_values(small_log, activity_key)
                    # append the concurrent activity as leaf:
                    self.children.append(
                        SubtreePlain(small_log, small_dfg, self.master_dfg, self.initial_dfg,
                                     small_activities,
                                     self.counts,
                                     self.rec_depth + 1,
                                     noise_threshold=self.noise_threshold,
                                     initial_start_activities=self.initial_start_activities,
                                     initial_end_activities=self.initial_end_activities,
                                     parameters=parameters))
                    # continue with the recursion on the new log:
                    start_activities = list(
                        start_activities_filter.get_start_activities(new_log, parameters=self.parameters).keys())
                    end_activities = list(
                        end_activities_filter.get_end_activities(new_log, parameters=self.parameters).keys())
                    self.children.append(
                        SubtreePlain(new_log, new_dfg, self.master_dfg, self.initial_dfg,
                                     activities,
                                     self.counts,
                                     self.rec_depth + 1,
                                     noise_threshold=self.noise_threshold,
                                     start_activities=start_activities,
                                     end_activities=end_activities,
                                     initial_start_activities=self.initial_start_activities,
                                     initial_end_activities=self.initial_end_activities,
                                     parameters=parameters))
                else:
                    if use_strict_tau_loop:
                        strict_tau_loop, new_log = fall_through.strict_tau_loop(self.log, self.start_activities,
                                                                                self.end_activities, activity_key)
                        new_log = filtering_utils.keep_one_trace_per_variant(new_log, parameters=parameters)
                    else:
                        strict_tau_loop = False
                    if use_strict_tau_loop and strict_tau_loop:
                        activites_left = []
                        for trace in new_log:
                            for act in trace:
                                if act[activity_key] not in activites_left:
                                    activites_left.append(act[activity_key])
                        self.detected_cut = 'strict_tau_loop'
                        new_dfg = [(k, v) for k, v in dfg_inst.apply(new_log, parameters=parameters).items() if
                                   v > 0]
                        activities = attributes_filter.get_attribute_values(new_log, activity_key)
                        start_activities = list(
                            start_activities_filter.get_start_activities(new_log, parameters=self.parameters).keys())
                        end_activities = list(
                            end_activities_filter.get_end_activities(new_log, parameters=self.parameters).keys())
                        self.children.append(
                            SubtreePlain(new_log, new_dfg, self.master_dfg, self.initial_dfg,
                                         activities,
                                         self.counts,
                                         self.rec_depth + 1,
                                         noise_threshold=self.noise_threshold,
                                         start_activities=start_activities,
                                         end_activities=end_activities,
                                         initial_start_activities=self.initial_start_activities,
                                         initial_end_activities=self.initial_end_activities,
                                         parameters=parameters))
                    else:
                        if use_tau_loop:
                            tau_loop, new_log = fall_through.tau_loop(self.log, self.start_activities, activity_key)
                            new_log = filtering_utils.keep_one_trace_per_variant(new_log, parameters=parameters)
                        else:
                            tau_loop = False
                        if use_tau_loop and tau_loop:
                            activites_left = []
                            for trace in new_log:
                                for act in trace:
                                    if act[activity_key] not in activites_left:
                                        activites_left.append(act[activity_key])
                            self.detected_cut = 'tau_loop'
                            new_dfg = [(k, v) for k, v in dfg_inst.apply(new_log, parameters=parameters).items() if
                                       v > 0]
                            activities = attributes_filter.get_attribute_values(new_log, activity_key)
                            start_activities = list(start_activities_filter.get_start_activities(new_log,
                                                                                                 parameters=self.parameters).keys())
                            end_activities = list(
                                end_activities_filter.get_end_activities(new_log, parameters=self.parameters).keys())
                            self.children.append(
                                SubtreePlain(new_log, new_dfg, self.master_dfg, self.initial_dfg,
                                             activities,
                                             self.counts,
                                             self.rec_depth + 1,
                                             noise_threshold=self.noise_threshold,
                                             start_activities=start_activities,
                                             end_activities=end_activities,
                                             initial_start_activities=self.initial_start_activities,
                                             initial_end_activities=self.initial_end_activities,
                                             parameters=parameters))
                        else:
                            logging.debug("flower model")
                            activites_left = []
                            for trace in self.log:
                                for act in trace:
                                    if act[activity_key] not in activites_left:
                                        activites_left.append(act[activity_key])
                            self.detected_cut = 'flower'
                            # apply flower fall through as last option:


def make_tree(log, dfg, master_dfg, initial_dfg, activities, c, recursion_depth, noise_threshold, start_activities,
              end_activities, initial_start_activities, initial_end_activities, parameters=None):
    tree = SubtreePlain(log, dfg, master_dfg, initial_dfg, activities, c, recursion_depth, noise_threshold,
                        start_activities,
                        end_activities, initial_start_activities, initial_end_activities, parameters=parameters)

    return tree

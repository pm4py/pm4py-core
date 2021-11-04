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
from copy import copy
from pm4py.algo.discovery.dfg.utils.dfg_utils import get_activities_from_dfg, \
    infer_start_activities, infer_end_activities
from pm4py.algo.discovery.dfg.utils.dfg_utils import get_ingoing_edges, get_outgoing_edges
from pm4py.algo.discovery.dfg.utils.dfg_utils import negate, get_activities_self_loop, transform_dfg_to_directed_nx_graph
from pm4py.algo.discovery.dfg.variants import native as dfg_inst
from pm4py.algo.filtering.dfg.dfg_filtering import clean_dfg_based_on_noise_thresh
from pm4py.algo.discovery.inductive.variants.im.util import base_case
from pm4py import util as pmutil
from pm4py.algo.discovery.inductive.variants.im.util import splitting as split
from pm4py.statistics.attributes.log import get as attributes_get
from pm4py.statistics.end_activities.log import get as end_activities_get
from pm4py.statistics.start_activities.log import get  as start_activities_get
from pm4py.algo.discovery.inductive.util import parallel_cut_utils, detection_utils, cut_detection
from pm4py.algo.discovery.inductive.variants.im_f import splitting_infrequent, fall_through_infrequent
from pm4py.algo.discovery.inductive.variants.im.util import fall_through
from pm4py.util import exec_utils
import pkgutil
import logging
from pm4py.util import constants
from enum import Enum


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    NOISE_THRESHOLD = "noiseThreshold"
    EMPTY_TRACE_KEY = "empty_trace"
    ONCE_PER_TRACE_KEY = "once_per_trace"
    CONCURRENT_KEY = "concurrent"
    STRICT_TAU_LOOP_KEY = "strict_tau_loop"
    TAU_LOOP_KEY = "tau_loop"


class SubtreeInfrequent(object):

    def __init__(self, log, dfg, master_dfg, initial_dfg, activities, counts, rec_depth, f=0, noise_threshold=0,
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
            self.f = f
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
            self.parameters = parameters

            self.initialize_tree(dfg, log, initial_dfg, activities)

    def __deepcopy__(self, memodict={}):
        """
            def __init__(self, log, dfg, master_dfg, initial_dfg, activities, counts, rec_depth, noise_threshold=0,
                 start_activities=None, end_activities=None, initial_start_activities=None,
                 initial_end_activities=None, parameters=None, real_init=False):
        :param memodict:
        :return:
        """
        S = SubtreeInfrequent(None, None, None, None, None, None, None, real_init=False)
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
        try:
            S.parameters = self.parameters
        except:
            pass
        return S

    def initialize_tree(self, dfg, log, initial_dfg, activities, second_iteration=False, end_call=True):
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
        # self.activities_direction = get_activities_direction(self.dfg, self.activities)
        # self.activities_dir_list = get_activities_dirlist(self.activities_direction)
        self.negated_dfg = negate(self.dfg)
        self.negated_activities = get_activities_from_dfg(self.negated_dfg)
        self.negated_outgoing = get_outgoing_edges(self.negated_dfg)
        self.negated_ingoing = get_ingoing_edges(self.negated_dfg)
        self.detected_cut = None
        self.children = []
        self.log = log

        self.detect_cut_if(second_iteration=False, parameters=self.parameters)

    def detect_xor(self, conn_components):
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
        if not self.contains_empty_trace() and len(conn_components) > 1:
            return [True, conn_components]

        return [False, []]

    def contains_empty_trace(self):
        contains = False
        for trace in self.log:
            if len(trace) == 0:
                contains = True
        return contains

    def detect_concurrent(self):
        if self.contains_empty_trace():
            return [False, []]
        inverted_dfg = []  # create an inverted dfg, the connected components of this dfg are the split
        for a in self.activities:
            for b in self.activities:
                if a != b:
                    if not (self.is_followed_by(self.dfg, a, b) and self.is_followed_by(self.dfg, b, a)):
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

    def detect_loop(self):
        # p0 is part of return value, it contains the partition of activities
        # write all start and end activities in p1
        if self.contains_empty_trace():
            return [False, []]
        start_activities = list(
            start_activities_get.get_start_activities(self.log, parameters=self.parameters).keys())
        end_activities = list(end_activities_get.get_end_activities(self.log, parameters=self.parameters).keys())
        p1 = []
        for act in start_activities:
            if act not in p1:
                p1.append(act)
        for act in end_activities:
            if act not in p1:
                p1.append(act)

        # create new dfg without the transitions to start and end activities
        new_dfg = copy(self.dfg)
        copy_dfg = copy(new_dfg)
        for ele in copy_dfg:
            if ele[0][0] in p1 or ele[0][1] in p1:
                new_dfg.remove(ele)
        # get connected components of this new dfg
        new_ingoing = get_ingoing_edges(new_dfg)
        new_outgoing = get_outgoing_edges(new_dfg)
        # it was a pain in the *** to get a working directory of the current_activities, as we can't iterate ove the dfg
        current_activities = {}
        for element in self.activities:
            if element not in p1:
                current_activities.update({element: 1})
        p0 = detection_utils.get_connected_components(new_ingoing, new_outgoing, current_activities)
        p0.insert(0, p1)

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
                    for e in end_activities:  # for every end activity
                        if e not in start_activities:
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
                    for s in start_activities:
                        if s not in end_activities:
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

        iterable_dfg = []
        for i in range(0, len(self.dfg)):
            iterable_dfg.append(self.dfg[i][0])

        p0_copy = []
        for int_el in p0:
            p0_copy.append(int_el)
        for element in p0_copy:
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

        if len(p0) > 1:
            return [True, p0]
        else:
            return [False, []]

    def is_followed_by(self, dfg, activity_a, activity_b):
        """
        check if Activity A is followed by Activity B in the dfg of self, returns bool.
        """
        for i in range(0, len(dfg)):
            if (activity_a, activity_b) == dfg[i][0]:
                return True

        return False

    def check_cut_im_plain(self):
        if pkgutil.find_loader("networkx"):
            import networkx as nx

            conn_components = detection_utils.get_connected_components(self.ingoing, self.outgoing, self.activities)
            this_nx_graph = transform_dfg_to_directed_nx_graph(self.dfg, activities=self.activities)
            strongly_connected_components = [list(x) for x in nx.strongly_connected_components(this_nx_graph)]
            xor_cut = self.detect_xor(conn_components)
            if xor_cut[0]:
                return True, 'concurrent', xor_cut
            else:
                sequence_cut = cut_detection.detect_sequential_cut(self, self.dfg, strongly_connected_components)
                if sequence_cut[0]:
                    return True, 'sequential', sequence_cut
                else:
                    parallel_cut = self.detect_concurrent()
                    if parallel_cut[0]:
                        return True, 'parallel', parallel_cut
                    else:
                        loop_cut = self.detect_loop()
                        if loop_cut[0]:
                            return True, 'loopCut', loop_cut
                        else:
                            return False, 'noCut', []
        else:
            msg = "networkx is not available. inductive miner cannot be used!"
            logging.error(msg)
            raise Exception(msg)

    def calculate_threshold(self, act):
        max_value = 0
        for element in self.dfg:
            if element[0][0] == act:
                if element[1] > max_value:
                    max_value = element[1]
        return max_value

    def filter_dfg_on_threshold(self):
        filtered_dfg = []
        for element in self.dfg:
            threshold = self.calculate_threshold(element[0][0]) * self.f
            if element[1] == threshold or element[1] > threshold:
                filtered_dfg.append(element)
        self.dfg = filtered_dfg

    def apply_cut_im_plain(self, type_of_cut, cut, activity_key):
        if type_of_cut == 'concurrent':
            self.detected_cut = 'concurrent'
            new_logs = split.split_xor(cut[1], self.log, activity_key)
            for l in new_logs:
                new_dfg = [(k, v) for k, v in dfg_inst.apply(l, parameters=self.parameters).items() if v > 0]
                activities = attributes_get.get_attribute_values(l, activity_key)
                start_activities = list(
                    start_activities_get.get_start_activities(l, parameters=self.parameters).keys())
                end_activities = list(
                    end_activities_get.get_end_activities(l, parameters=self.parameters).keys())
                self.children.append(
                    SubtreeInfrequent(l, new_dfg, self.master_dfg, self.initial_dfg, activities, self.counts,
                                      self.rec_depth + 1, self.f,
                                      noise_threshold=self.noise_threshold, start_activities=start_activities,
                                      end_activities=end_activities,
                                      initial_start_activities=self.initial_start_activities,
                                      initial_end_activities=self.initial_end_activities, parameters=self.parameters))
        elif type_of_cut == 'sequential':
            new_logs = split.split_sequence(cut[1], self.log, activity_key)
            self.detected_cut = "sequential"
            for l in new_logs:
                new_dfg = [(k, v) for k, v in dfg_inst.apply(l, parameters=self.parameters).items() if v > 0]
                activities = attributes_get.get_attribute_values(l, activity_key)
                start_activities = list(
                    start_activities_get.get_start_activities(l, parameters=self.parameters).keys())
                end_activities = list(
                    end_activities_get.get_end_activities(l, parameters=self.parameters).keys())
                self.children.append(
                    SubtreeInfrequent(l, new_dfg, self.master_dfg, self.initial_dfg, activities, self.counts,
                                      self.rec_depth + 1, self.f,
                                      noise_threshold=self.noise_threshold, start_activities=start_activities,
                                      end_activities=end_activities,
                                      initial_start_activities=self.initial_start_activities,
                                      initial_end_activities=self.initial_end_activities, parameters=self.parameters))
        elif type_of_cut == 'parallel':
            new_logs = split.split_parallel(cut[1], self.log, activity_key)
            self.detected_cut = "parallel"
            for l in new_logs:
                new_dfg = [(k, v) for k, v in dfg_inst.apply(l, parameters=self.parameters).items() if v > 0]
                activities = attributes_get.get_attribute_values(l, activity_key)
                start_activities = list(
                    start_activities_get.get_start_activities(l, parameters=self.parameters).keys())
                end_activities = list(
                    end_activities_get.get_end_activities(l, parameters=self.parameters).keys())
                self.children.append(
                    SubtreeInfrequent(l, new_dfg, self.master_dfg, self.initial_dfg, activities, self.counts,
                                      self.rec_depth + 1, self.f,
                                      noise_threshold=self.noise_threshold, start_activities=start_activities,
                                      end_activities=end_activities,
                                      initial_start_activities=self.initial_start_activities,
                                      initial_end_activities=self.initial_end_activities, parameters=self.parameters))
        elif type_of_cut == 'loopCut':
            new_logs = split.split_loop(cut[1], self.log, activity_key)
            self.detected_cut = "loopCut"
            for l in new_logs:
                new_dfg = [(k, v) for k, v in dfg_inst.apply(l, parameters=self.parameters).items() if v > 0]
                activities = attributes_get.get_attribute_values(l, activity_key)
                start_activities = list(
                    start_activities_get.get_start_activities(l, parameters=self.parameters).keys())
                end_activities = list(
                    end_activities_get.get_end_activities(l, parameters=self.parameters).keys())
                self.children.append(
                    SubtreeInfrequent(l, new_dfg, self.master_dfg, self.initial_dfg, activities, self.counts,
                                      self.rec_depth + 1, self.f,
                                      noise_threshold=self.noise_threshold,
                                      start_activities=start_activities,
                                      end_activities=end_activities,
                                      initial_start_activities=self.initial_start_activities,
                                      initial_end_activities=self.initial_end_activities, parameters=self.parameters))

    def detect_cut_if(self, second_iteration=False, parameters=None):
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
        # use the cutting and splitting functions of im_plain:
        else:
            found_plain_cut, type_of_cut, cut = self.check_cut_im_plain()

            if found_plain_cut:
                self.apply_cut_im_plain(type_of_cut, cut, activity_key)
            # if im_plain does not find a cut, we filter on our threshold and then again apply the im_cut detection
            # but this time, we have to use different splitting functions:
            else:
                self.filter_dfg_on_threshold()
                found_plain_cut, type_of_cut, cut = self.check_cut_im_plain()
                if found_plain_cut:
                    if type_of_cut == 'concurrent':
                        logging.debug("concurrent_cut_if")
                        self.detected_cut = 'concurrent'
                        new_logs = splitting_infrequent.split_xor_infrequent(cut[1], self.log, activity_key)
                        for l in new_logs:
                            new_dfg = [(k, v) for k, v in dfg_inst.apply(l, parameters=parameters).items() if v > 0]
                            activities = attributes_get.get_attribute_values(l, activity_key)
                            start_activities = list(
                                start_activities_get.get_start_activities(l, parameters=parameters).keys())
                            end_activities = list(
                                end_activities_get.get_end_activities(l, parameters=parameters).keys())
                            self.children.append(
                                SubtreeInfrequent(l, new_dfg, self.master_dfg, self.initial_dfg, activities,
                                                  self.counts,
                                                  self.rec_depth + 1, self.f,
                                                  noise_threshold=self.noise_threshold,
                                                  start_activities=start_activities,
                                                  end_activities=end_activities,
                                                  initial_start_activities=self.initial_start_activities,
                                                  initial_end_activities=self.initial_end_activities,
                                                  parameters=parameters))
                    elif type_of_cut == 'sequential':
                        logging.debug("sequential_if")
                        new_logs = splitting_infrequent.split_sequence_infrequent(cut[1], self.log, activity_key)
                        self.detected_cut = "sequential"
                        for l in new_logs:
                            new_dfg = [(k, v) for k, v in dfg_inst.apply(l, parameters=parameters).items() if v > 0]
                            activities = attributes_get.get_attribute_values(l, activity_key)
                            start_activities = list(
                                start_activities_get.get_start_activities(l, parameters=parameters).keys())
                            end_activities = list(
                                end_activities_get.get_end_activities(l, parameters=parameters).keys())
                            self.children.append(
                                SubtreeInfrequent(l, new_dfg, self.master_dfg, self.initial_dfg, activities,
                                                  self.counts,
                                                  self.rec_depth + 1, self.f,
                                                  noise_threshold=self.noise_threshold,
                                                  start_activities=start_activities,
                                                  end_activities=end_activities,
                                                  initial_start_activities=self.initial_start_activities,
                                                  initial_end_activities=self.initial_end_activities,
                                                  parameters=parameters))
                    elif type_of_cut == 'parallel':
                        logging.debug("parallel_if")
                        new_logs = split.split_parallel(cut[1], self.log, activity_key)
                        self.detected_cut = "parallel"
                        for l in new_logs:
                            new_dfg = [(k, v) for k, v in dfg_inst.apply(l, parameters=parameters).items() if v > 0]
                            activities = attributes_get.get_attribute_values(l, activity_key)
                            start_activities = list(
                                start_activities_get.get_start_activities(l, parameters=parameters).keys())
                            end_activities = list(
                                end_activities_get.get_end_activities(l, parameters=parameters).keys())
                            self.children.append(
                                SubtreeInfrequent(l, new_dfg, self.master_dfg, self.initial_dfg, activities,
                                                  self.counts,
                                                  self.rec_depth + 1, self.f,
                                                  noise_threshold=self.noise_threshold,
                                                  start_activities=start_activities,
                                                  end_activities=end_activities,
                                                  initial_start_activities=self.initial_start_activities,
                                                  initial_end_activities=self.initial_end_activities,
                                                  parameters=parameters))
                    elif type_of_cut == 'loopCut':
                        logging.debug("loopCut_if")
                        new_logs = splitting_infrequent.split_loop_infrequent(cut[1], self.log, activity_key)
                        self.detected_cut = "loopCut"
                        for l in new_logs:
                            new_dfg = [(k, v) for k, v in dfg_inst.apply(l, parameters=parameters).items() if v > 0]
                            activities = attributes_get.get_attribute_values(l, activity_key)
                            start_activities = list(
                                start_activities_get.get_start_activities(l, parameters=parameters).keys())
                            end_activities = list(
                                end_activities_get.get_end_activities(l, parameters=parameters).keys())
                            self.children.append(
                                SubtreeInfrequent(l, new_dfg, self.master_dfg, self.initial_dfg, activities,
                                                  self.counts,
                                                  self.rec_depth + 1, self.f,
                                                  noise_threshold=self.noise_threshold,
                                                  start_activities=start_activities,
                                                  end_activities=end_activities,
                                                  initial_start_activities=self.initial_start_activities,
                                                  initial_end_activities=self.initial_end_activities,
                                                  parameters=parameters))

                else:
                    self.apply_fall_through_infrequent(parameters)

    def apply_fall_through_infrequent(self, parameters=None):
        if parameters is None:
            parameters = {}
        activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, self.parameters,
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
            empty_traces_present, enough_traces, new_log = fall_through_infrequent.empty_trace_filtering(self.log, self.f)
            self.log = new_log
        else:
            empty_traces_present = False
            enough_traces = False
        # if an empty trace is found, the empty trace fallthrough applies
        if empty_traces_present and enough_traces:
            logging.debug("empty_trace_if")
            self.detected_cut = 'empty_trace'
            new_dfg = [(k, v) for k, v in dfg_inst.apply(new_log, parameters=self.parameters).items() if v > 0]
            activities = attributes_get.get_attribute_values(new_log, activity_key)
            start_activities = list(
                                start_activities_get.get_start_activities(new_log, parameters=parameters).keys())
            end_activities = list(
                                end_activities_get.get_end_activities(new_log, parameters=parameters).keys())
            self.children.append(
                SubtreeInfrequent(new_log, new_dfg, self.master_dfg, self.initial_dfg, activities, self.counts,
                                  self.rec_depth + 1, self.f,
                                  noise_threshold=self.noise_threshold,
                                  start_activities=start_activities,
                                  end_activities=end_activities,
                                  initial_start_activities=self.initial_start_activities,
                                  initial_end_activities=self.initial_end_activities, parameters=parameters))
        elif empty_traces_present and not enough_traces:
            # no node is added to the PT, instead we just use recursion on the log without the empty traces
            self.detect_cut_if(parameters=parameters)
        else:
            if use_act_once_per_trace:
                activity_once, new_log, small_log = fall_through.act_once_per_trace(self.log, self.activities, activity_key)
            else:
                activity_once = False
            if activity_once:
                self.detected_cut = 'parallel'
                # create two new dfgs as we need them to append to self.children later
                new_dfg = [(k, v) for k, v in dfg_inst.apply(new_log, parameters=parameters).items() if
                           v > 0]
                activities = attributes_get.get_attribute_values(new_log, activity_key)
                small_dfg = [(k, v) for k, v in dfg_inst.apply(small_log, parameters=parameters).items() if
                             v > 0]
                small_activities = attributes_get.get_attribute_values(small_log, activity_key)
                start_activities = list(
                                start_activities_get.get_start_activities(new_log, parameters=parameters).keys())
                end_activities = list(
                                end_activities_get.get_end_activities(new_log, parameters=parameters).keys())
                # append the chosen activity as leaf:
                self.children.append(
                    SubtreeInfrequent(small_log, small_dfg, self.master_dfg, self.initial_dfg, small_activities,
                                      self.counts,
                                      self.rec_depth + 1, self.f,
                                      noise_threshold=self.noise_threshold,
                                      initial_start_activities=self.initial_start_activities,
                                      initial_end_activities=self.initial_end_activities, parameters=parameters))
                # continue with the recursion on the new log
                self.children.append(
                    SubtreeInfrequent(new_log, new_dfg, self.master_dfg, self.initial_dfg, activities,
                                      self.counts,
                                      self.rec_depth + 1, self.f,
                                      noise_threshold=self.noise_threshold,
                                      start_activities=start_activities,
                                      end_activities=end_activities,
                                      initial_start_activities=self.initial_start_activities,
                                      initial_end_activities=self.initial_end_activities, parameters=parameters))

            else:
                if use_act_concurrent:
                    activity_concurrent, new_log, small_log, key = fall_through.activity_concurrent(self, self.log,
                                                                                                self.activities,
                                                                                                activity_key,
                                                                                                parameters=parameters)
                else:
                    activity_concurrent = False
                if activity_concurrent:
                    self.detected_cut = 'parallel'
                    # create two new dfgs on to append later
                    new_dfg = [(k, v) for k, v in dfg_inst.apply(new_log, parameters=parameters).items() if
                               v > 0]
                    activities = attributes_get.get_attribute_values(new_log, activity_key)
                    small_dfg = [(k, v) for k, v in dfg_inst.apply(small_log, parameters=parameters).items() if
                                 v > 0]
                    small_activities = attributes_get.get_attribute_values(small_log, activity_key)
                    start_activities = list(
                                start_activities_get.get_start_activities(new_log, parameters=parameters).keys())
                    end_activities = list(
                                end_activities_get.get_end_activities(new_log, parameters=parameters).keys())
                    # append the concurrent activity as leaf:
                    self.children.append(
                        SubtreeInfrequent(small_log, small_dfg, self.master_dfg, self.initial_dfg,
                                          small_activities,
                                          self.counts,
                                          self.rec_depth + 1, self.f,
                                          noise_threshold=self.noise_threshold,
                                          initial_start_activities=self.initial_start_activities,
                                          initial_end_activities=self.initial_end_activities, parameters=parameters))
                    # continue with the recursion on the new log:
                    self.children.append(
                        SubtreeInfrequent(new_log, new_dfg, self.master_dfg, self.initial_dfg,
                                          activities,
                                          self.counts,
                                          self.rec_depth + 1, self.f,
                                          noise_threshold=self.noise_threshold,
                                          start_activities=start_activities,
                                          end_activities=end_activities,
                                          initial_start_activities=self.initial_start_activities,
                                          initial_end_activities=self.initial_end_activities, parameters=parameters))
                else:
                    if use_strict_tau_loop:
                        strict_tau_loop, new_log = fall_through.strict_tau_loop(self.log, self.start_activities,
                                                                            self.end_activities, activity_key)
                    else:
                        strict_tau_loop = False
                    if strict_tau_loop:
                        self.detected_cut = 'strict_tau_loop'
                        new_dfg = [(k, v) for k, v in dfg_inst.apply(new_log, parameters=parameters).items() if
                                   v > 0]
                        activities = attributes_get.get_attribute_values(new_log, activity_key)
                        start_activities = list(
                                start_activities_get.get_start_activities(new_log, parameters=parameters).keys())
                        end_activities = list(
                                end_activities_get.get_end_activities(new_log, parameters=parameters).keys())
                        self.children.append(
                            SubtreeInfrequent(new_log, new_dfg, self.master_dfg, self.initial_dfg,
                                              activities,
                                              self.counts,
                                              self.rec_depth + 1, self.f,
                                              noise_threshold=self.noise_threshold,
                                              start_activities=start_activities,
                                              end_activities=end_activities,
                                              initial_start_activities=self.initial_start_activities,
                                              initial_end_activities=self.initial_end_activities,
                                              parameters=parameters))
                    else:
                        if use_tau_loop:
                            tau_loop, new_log = fall_through.tau_loop(self.log, self.start_activities, activity_key)
                        else:
                            tau_loop = False
                        if tau_loop:
                            self.detected_cut = 'tau_loop'
                            new_dfg = [(k, v) for k, v in dfg_inst.apply(new_log, parameters=parameters).items() if
                                       v > 0]
                            activities = attributes_get.get_attribute_values(new_log, activity_key)
                            start_activities = list(
                                start_activities_get.get_start_activities(new_log, parameters=parameters).keys())
                            end_activities = list(
                                end_activities_get.get_end_activities(new_log, parameters=parameters).keys())
                            self.children.append(
                                SubtreeInfrequent(new_log, new_dfg, self.master_dfg, self.initial_dfg,
                                                  activities,
                                                  self.counts,
                                                  self.rec_depth + 1, self.f,
                                                  noise_threshold=self.noise_threshold,
                                                  start_activities=start_activities,
                                                  end_activities=end_activities,
                                                  initial_start_activities=self.initial_start_activities,
                                                  initial_end_activities=self.initial_end_activities,
                                                  parameters=parameters))
                        else:
                            logging.debug("flower_if")
                            self.detected_cut = 'flower'
                            # apply flower fall through as last option:


def make_tree(log, dfg, master_dfg, initial_dfg, activities, c, f, recursion_depth, noise_threshold, start_activities,
              end_activities, initial_start_activities, initial_end_activities, parameters=None):
    if parameters is None:
        parameters = {}

    tree = SubtreeInfrequent(log, dfg, master_dfg, initial_dfg, activities, c, f, recursion_depth, noise_threshold,
                             start_activities, end_activities, initial_start_activities, initial_end_activities,
                             parameters=parameters)
    return tree

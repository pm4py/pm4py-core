from pm4py.entities.log.util import trace_log as tl_util
from pm4py.algo.discovery.dfg.versions import native as dfg_inst
from pm4py.entities import petri
from pm4py.entities.petri.petrinet import Marking
import time
from copy import copy
import sys
from pm4py.entities.petri.petrinet import PetriNet
from collections import Counter
from pm4py import util as pmutil
from pm4py.entities.log.util import xes as xes_util
from pm4py.algo.discovery.dfg.utils.dfg_utils import get_ingoing_edges, get_outgoing_edges, get_activities_from_dfg
from pm4py.algo.filtering.dfg.dfg_filtering import clean_dfg_based_on_noise_thresh
from pm4py.algo.conformance.tokenreplay import factory as token_replay
from pm4py.algo.repair.petri_reduction import factory as reduction

sys.setrecursionlimit(100000)

def apply(trace_log, parameters):
    """
    Apply the IMDF algorithm to a log

    Parameters
    -----------
    trace_log
        Trace log
    parameters
        Parameters of the algorithm

    Returns
    -----------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    if parameters is None:
        parameters = {}
    if not pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY
    activity_key = parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]
    # apply the reduction by default only on very small logs
    enable_reduction = parameters["enable_reduction"] if "enable_reduction" in parameters else len(trace_log) < 30

    indMinDirFollows = InductMinDirFollows()
    net, initial_marking, final_marking = indMinDirFollows.apply(trace_log, parameters, activity_key=activity_key)

    # clean net from duplicate hidden transitions
    net = clean_duplicate_transitions(net)

    if enable_reduction:
        # do the replay
        aligned_traces = token_replay.apply(trace_log, net, initial_marking, final_marking, parameters=parameters)

        # apply petri_reduction technique in order to simplify the Petri net
        net = reduction.apply(net, parameters={"aligned_traces": aligned_traces})

    return net, initial_marking, final_marking

def clean_duplicate_transitions(net):
    """
    Clean duplicate transitions in a Petri net

    Parameters
    ------------
    net
        Petri net

    Returns
    ------------
    net
        Cleaned Petri net
    """
    transitions = list(net.transitions)
    alreadyVisitedCombo = set()
    # while cycle because we have to delete some of them
    i = 0
    while i < len(transitions):
        trans = transitions[i]
        if trans.label is None:
            in_arcs = trans.in_arcs
            out_arcs = trans.out_arcs
            to_delete = False
            for in_arc in in_arcs:
                in_place = in_arc.source
                for out_arc in out_arcs:
                    out_place = out_arc.target
                    combo = in_place.name + " " + out_place.name
                    if combo in alreadyVisitedCombo:
                        to_delete = True
                        break
                    alreadyVisitedCombo.add(combo)
            if to_delete:
                net = petri.utils.remove_transition(net, trans)
        i = i + 1
    return net

def apply_dfg(dfg, parameters):
    """
    Apply the IMDF algorithm to a DFG graph

    Parameters
    -----------
    dfg
        Directly-Follows graph
    parameters
        Parameters of the algorithm

    Returns
    -----------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    if parameters is None:
        parameters = {}
    if not pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY
    activity_key = parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]
    indMinDirFollows = InductMinDirFollows()
    net, initial_marking, final_marking = indMinDirFollows.apply_dfg(dfg, parameters, activity_key=activity_key)

    # clean net from duplicate hidden transitions
    net = clean_duplicate_transitions(net)

    return net, initial_marking, final_marking

class Counts(object):
    """
    Shared variables among executions
    """
    def __init__(self):
        """
        Constructor
        """
        self.noOfPlaces = 0
        self.noOfHiddenTransitions = 0
        self.noOfVisibleTransitions = 0
        self.dictSkips = {}
        self.dictLoops = {}

    def inc_places(self):
        """
        Increase the number of places
        """
        self.noOfPlaces = self.noOfPlaces + 1

    def inc_noOfHidden(self):
        """
        Increase the number of hidden transitions
        """
        self.noOfHiddenTransitions = self.noOfHiddenTransitions + 1

    def inc_noOfVisible(self):
        """
        Increase the number of visible transitions
        """
        self.noOfVisibleTransitions = self.noOfVisibleTransitions + 1

class Subtree(object):
    def __init__(self, dfg, initialDfg, activities, counts, recDepth, noiseThreshold=0):
        """
        Constructor

        Parameters
        -----------
        dfg
            Directly follows graph of this subtree
        initialDfg
            Referral directly follows graph that should be taken in account adding hidden/loop transitions
        activities
            Activities of this subtree
        counts
            Shared variable
        recDepth
            Current recursion depth
        """

        self.initialDfg = copy(initialDfg)
        self.counts = counts
        self.recDepth = recDepth
        self.noiseThreshold = noiseThreshold

        self.initialize_tree(dfg, initialDfg, activities)

    def initialize_tree(self, dfg, initialDfg, activities, secondIteration=False):
        """
        Initialize the tree


        Parameters
        -----------
        dfg
            Directly follows graph of this subtree
        initialDfg
            Referral directly follows graph that should be taken in account adding hidden/loop transitions
        activities
            Activities of this subtree
        """

        self.secondIteration = secondIteration

        if activities is None:
            self.activities = get_activities_from_dfg(dfg)
        else:
            self.activities = copy(activities)

        if secondIteration:
            self.dfg = clean_dfg_based_on_noise_thresh(self.dfg, self.activities, self.noiseThreshold)
        else:
            self.dfg = copy(dfg)

        self.outgoing = get_outgoing_edges(self.dfg)
        self.ingoing = get_ingoing_edges(self.dfg)
        self.selfLoopActivities = self.get_activities_self_loop()
        self.initialOutgoing = get_outgoing_edges(self.initialDfg)
        self.initialIngoing = get_ingoing_edges(self.initialDfg)
        self.activitiesDirection = self.get_activities_direction()
        self.activitiesDirlist = self.get_activities_dirlist()
        self.negatedDfg = self.negate()
        self.negatedActivities = get_activities_from_dfg(self.negatedDfg)
        self.negatedOutgoing = get_outgoing_edges(self.negatedDfg)
        self.negatedIngoing = get_ingoing_edges(self.negatedDfg)
        self.detectedCut = None
        self.children = []

        self.detect_cut(secondIteration=secondIteration)

    def negate(self):
        """
        Negate relationship in the DFG graph
        :return:
        """
        negatedDfg = []

        for el in self.dfg:
            if not(el[0][1] in self.outgoing and el[0][0] in self.outgoing[el[0][1]]):
                negatedDfg.append(el)

        activitiesThatAreNotNegatedDfg = set(set(self.activities)).difference(get_activities_from_dfg(negatedDfg))

        return negatedDfg

    def get_activities_self_loop(self):
        """
        Get attributes that are in self-loop in this subtree
        """
        self_loop_act = []
        for act in self.outgoing:
            if act in list(self.outgoing[act].keys()):
                self_loop_act.append(act)
        return self_loop_act

    def get_activities_direction(self):
        """
        Calculate attributes direction (Heuristics Miner)
        """
        direction = {}
        for act in self.activities:
            outgoing = 0
            ingoing = 0
            if act in self.outgoing:
                outgoing = sum(list(self.outgoing[act].values()))
            if act in self.ingoing:
                ingoing = sum(list(self.ingoing[act].values()))
            dependency = (outgoing - ingoing)/(ingoing + outgoing + 1)
            direction[act] = dependency
        return direction

    def get_activities_dirlist(self):
        """
        Activities direction list
        """
        dirlist = []
        for act in self.activitiesDirection:
            dirlist.append([act, self.activitiesDirection[act]])
        dirlist = sorted(dirlist, key=lambda x: (x[1], x[0]), reverse=True)
        return dirlist

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
        hasOutgoingConnInSet1 = False
        if act[0] in self.outgoing:
            for act2 in self.outgoing[act[0]]:
                if act2 in set1:
                    hasOutgoingConnInSet1 = True
        hasIngoingConnInSet2 = False
        if act[0] in self.ingoing:
            for act2 in self.ingoing[act[0]]:
                if act2 in set2:
                    hasIngoingConnInSet2 = True

        if hasOutgoingConnInSet1 and hasIngoingConnInSet2:
            return [False, set1, set2]

        if hasOutgoingConnInSet1:
            set1.add(act[0])
        elif hasIngoingConnInSet2:
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

        if len(self.activitiesDirlist) > 0:
            set1.add(self.activitiesDirlist[0][0])
        if len(self.activitiesDirlist) > -1:
            if not (self.activitiesDirlist[0][0] in self.ingoing and self.activitiesDirlist[-1][0] in self.ingoing[self.activitiesDirlist[0][0]]):
                set2.add(self.activitiesDirlist[-1][0])
            else:
                return [False, [], []]
        i = 1
        while i < len(self.activitiesDirlist)-1:
            act = self.activitiesDirlist[i]
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

        connectedComponents = []

        for act in ingoing:
            ingoing_act = set(ingoing[act].keys())
            if act in outgoing:
                ingoing_act = ingoing_act.union(set(outgoing[act].keys()))

            ingoing_act.add(act)

            if not ingoing_act in connectedComponents:
                connectedComponents.append(ingoing_act)
                activities_considered = activities_considered.union(set(ingoing_act))

        for act in outgoing:
            if not act in ingoing:
                outgoing_act = set(outgoing[act].keys())
                outgoing_act.add(act)
                if not outgoing_act in connectedComponents:
                    connectedComponents.append(outgoing_act)
                activities_considered = activities_considered.union(set(outgoing_act))

        something_changed = True
        it = 0
        while something_changed:
            it = it + 1
            something_changed = False

            oldConnectedComponents = copy(connectedComponents)
            connectedComponents = 0
            connectedComponents = []

            i = 0
            while i < len(oldConnectedComponents):
                conn1 = oldConnectedComponents[i]
                j = i + 1
                while j < len(oldConnectedComponents):
                    conn2 = oldConnectedComponents[j]
                    inte = conn1.intersection(conn2)

                    if len(inte) > 0:
                        conn1 = conn1.union(conn2)
                        something_changed = True
                        del oldConnectedComponents[j]
                        continue
                    j = j + 1

                if not conn1 in connectedComponents:
                    connectedComponents.append(conn1)
                i = i + 1

        if len(connectedComponents) == 0:
            for activity in activities:
                connectedComponents.append([activity])

        return connectedComponents

    def checkParCut(self, conn_components):
        """
        Checks if in a parallel cut all relations are present

        Parameters
        -----------
        conn_components
            Connected components
        """
        i = 0
        while i < len(conn_components):
            conn1 = conn_components[i]
            j = i + 1
            while j < len(conn_components):
                conn2 = conn_components[j]

                for act1 in conn1:
                    for act2 in conn2:
                        if not((act1 in self.outgoing and act2 in self.outgoing[act1]) and (act1 in self.ingoing and act2 in self.ingoing[act1])):
                            return False
                j = j + 1
            i = i + 1
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
        conn_components = self.get_connected_components(self.negatedIngoing, self.negatedOutgoing, self.activities)

        if len(conn_components) > 1:
            if self.checkParCut(conn_components):
                return [True, conn_components]

        return [False, []]

    def detect_loop_cut(self, dfg):
        """
        Detect loop cut
        """
        LOOP_CONST_1 = 0.2
        LOOP_CONST_2 = 0.02
        LOOP_CONST_3 = -0.2
        LOOP_CONST_4 = -0.7

        if len(self.activitiesDirlist) > 1:
            set1 = set()
            set2 = set()

            if self.activitiesDirlist[0][1] > LOOP_CONST_1:
                if self.activitiesDirlist[0][0] in self.ingoing:
                    activInput = list(self.ingoing[self.activitiesDirlist[0][0]])
                    for act in activInput:
                        if not act == self.activitiesDirlist[0][0] and self.activitiesDirection[act] < LOOP_CONST_2:
                            set2.add(act)

            if self.activitiesDirlist[-1][1] < LOOP_CONST_4:
                set2.add(self.activitiesDirlist[-1][0])

            if len(set2) > 0:
                for act in self.activities:
                    if not act in set2 or act in set1:
                        if self.activitiesDirection[act] < LOOP_CONST_3:
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
            sum = 0
            for act1 in comp:
                if act1 in ingoing and act2 in ingoing[act1]:
                   sum = sum + ingoing[act1][act2]
                if act1 in outgoing and act2 in outgoing[act1]:
                    sum = sum + outgoing[act1][act2]
            sums.append(sum)
            if sums[-1] > sums[idx_max_sum]:
                idx_max_sum = len(sums)-1

        comps[idx_max_sum].add(act2)

        return comps

    def detect_cut(self, secondIteration=False):
        """
        Detect generally a cut in the graph (applying all the algorithms)
        """
        if self.dfg:
            parCut = self.detect_parallel_cut()
            concCut = self.detect_concurrent_cut()
            seqCut = self.detect_sequential_cut(self.dfg)
            loopCut = self.detect_loop_cut(self.dfg)

            if parCut[0]:
                union_acti_comp = set()
                for comp in parCut[1]:
                    union_acti_comp = union_acti_comp.union(comp)
                diff_acti_comp = set(self.activities).difference(union_acti_comp)

                for act in diff_acti_comp:
                    parCut[1] = self.add_to_most_probable_component(parCut[1], act, self.ingoing, self.outgoing)

                for comp in parCut[1]:
                    newDfg = self.filter_dfg_on_act(self.dfg, comp)
                    self.detectedCut = "parallel"
                    self.children.append(Subtree(newDfg, self.initialDfg, comp, self.counts, self.recDepth + 1, noiseThreshold=self.noiseThreshold))
            else:
                if concCut[0]:
                    for comp in concCut[1]:
                        newDfg = self.filter_dfg_on_act(self.dfg, comp)
                        self.detectedCut = "concurrent"
                        self.children.append(Subtree(newDfg, self.initialDfg, comp, self.counts, self.recDepth + 1, noiseThreshold=self.noiseThreshold))
                else:
                    if seqCut[0]:
                        dfg1 = self.filter_dfg_on_act(self.dfg, seqCut[1])
                        dfg2 = self.filter_dfg_on_act(self.dfg, seqCut[2])
                        self.detectedCut = "sequential"
                        self.children.append(Subtree(dfg1, self.initialDfg, seqCut[1], self.counts, self.recDepth+1, noiseThreshold=self.noiseThreshold))
                        self.children.append(Subtree(dfg2, self.initialDfg, seqCut[2], self.counts, self.recDepth+1, noiseThreshold=self.noiseThreshold))
                    else:
                        if loopCut[0]:
                            dfg1 = self.filter_dfg_on_act(self.dfg, loopCut[1])
                            dfg2 = self.filter_dfg_on_act(self.dfg, loopCut[2])
                            self.detectedCut = "loopCut"
                            self.children.append(Subtree(dfg1, self.initialDfg, loopCut[1], self.counts, self.recDepth + 1, noiseThreshold=self.noiseThreshold))
                            self.children.append(Subtree(dfg2, self.initialDfg, loopCut[2], self.counts, self.recDepth + 1, noiseThreshold=self.noiseThreshold))
                        else:
                            if self.noiseThreshold > 0:
                                if not secondIteration:
                                    self.initialize_tree(self.dfg, self.initialDfg, None, secondIteration=True)
                            else:
                                pass
                            self.detectedCut = "flower"
        else:
            self.detectedCut = "base_concurrent"

    def filter_dfg_on_act(self, dfg, listact):
        """
        Filter a DFG graph on a list of attributes
        (to produce a projected DFG graph)

        Parameters
        -----------
        dfg
            Current DFG graph
        listact
            List of attributes to filter on
        """
        newDfg = []
        for el in dfg:
            if el[0][0] in listact and el[0][1] in listact:
                newDfg.append(el)
        return newDfg

    def get_new_place(self):
        """
        Create a new place in the Petri net
        """
        self.counts.inc_places()
        return petri.petrinet.PetriNet.Place('p_' + str(self.counts.noOfPlaces))

    def get_new_hidden_trans(self, type="unknown"):
        """
        Create a new hidden transition in the Petri net
        """
        self.counts.inc_noOfHidden()
        return petri.petrinet.PetriNet.Transition(type+'_' + str(self.counts.noOfHiddenTransitions), None)

    def get_transition(self, label):
        """
        Create a transitions with the specified label in the Petri net
        """
        self.counts.inc_noOfVisible()
        return petri.petrinet.PetriNet.Transition(label, label)

    def getSumValuesActivity(self, dict, activity):
        """
        Gets the sum of ingoing/outgoing values of an activity

        Parameters
        -----------
        dict
            Dictionary
        activity
            Current examined activity

        Returns
        -----------
        sum
        """
        sum = 0
        for act2 in dict[activity]:
            sum += dict[activity][act2]
        return sum

    def getMaxValue(self, dfg):
        """
        Get maximum ingoing/outgoing sum of values related to attributes in DFG graph
        """
        ingoing = get_ingoing_edges(dfg)
        outgoing = get_outgoing_edges(dfg)
        max_value = -1

        for act in ingoing:
            sum = self.getSumValuesActivity(ingoing, act)
            if sum > max_value:
                max_value = sum

        for act in outgoing:
            sum = self.getSumValuesActivity(outgoing, act)
            if sum > max_value:
                max_value = sum

        return max_value

    def getMaxValueWithActivitiesSpecification(self, dfg, activities):
        """
        Get maximum ingoing/outgoing sum of values related to attributes in DFG graph
        (here attributes to consider are specified)
        """
        ingoing = get_ingoing_edges(dfg)
        outgoing = get_outgoing_edges(dfg)
        max_value = -1

        for act in activities:
            if act in ingoing:
                sum = self.getSumValuesActivity(ingoing, act)
                if sum > max_value:
                    max_value = sum
            if act in outgoing:
                sum = self.getSumValuesActivity(outgoing, act)
                if sum > max_value:
                    max_value = sum

        return max_value

    def getSumStartActivitiesCount(self, dfg):
        """
        Gets the sum of start attributes count inside a DFG

        Parameters
        -------------
        dfg
            Directly-Follows graph

        Returns
        -------------
            Sum of start attributes count
        """
        ingoing = get_ingoing_edges(dfg)
        outgoing = get_outgoing_edges(dfg)

        sum_values = 0

        for act in outgoing:
            if not act in ingoing:
                for act2 in outgoing[act]:
                    sum_values += outgoing[act][act2]

        return sum_values

    def getSumEndActivitiesCount(self, dfg):
        """
        Gets the sum of end attributes count inside a DFG

        Parameters
        -------------
        dfg
            Directly-Follows graph

        Returns
        -------------
            Sum of start attributes count
        """
        ingoing = get_ingoing_edges(dfg)
        outgoing = get_outgoing_edges(dfg)

        sum_values = 0

        for act in ingoing:
            if not act in outgoing:
                for act2 in ingoing[act]:
                    sum_values += ingoing[act][act2]

        return sum_values

    def sumActivitiesCount(self, dfg, activities):
        """
        Gets the sum of specified attributes count inside a DFG

        Parameters
        -------------
        dfg
            Directly-Follows graph
        activities
            Activities to sum

        Returns
        -------------
            Sum of start attributes count
        """
        ingoing = get_ingoing_edges(dfg)
        outgoing = get_outgoing_edges(dfg)

        sum_values = 0

        for act in activities:
            if act in outgoing:
                for act2 in outgoing[act]:
                    sum_values += outgoing[act][act2]
            if act in ingoing:
                for act2 in ingoing[act]:
                    sum_values += ingoing[act][act2]
            if act in ingoing and act in outgoing:
                sum_values = int(sum_values / 2)

        return sum_values

    def verify_skip_transition_necessity(self, mAddSkip, initialDfg, dfg, childrenDfg, activities, childrenActivities, initial_connect_to):
        """
        Utility functions that decides if the skip transition is necessary

        Parameters
        ----------
        mAddSkip
            Boolean value, provided by the parent caller, that tells if the skip is absolutely necessary
        initialDfg
            Initial DFG
        dfg
            Directly follows graph
        childrenDfg
            Children DFG
        """
        if initial_connect_to.name == "p_1":
            return False
        if mAddSkip:
            return True

        maxValue = self.getMaxValue(initialDfg)
        sumStartActivitiesCount = self.getSumStartActivitiesCount(initialDfg)
        endActivitiesCount = self.getSumEndActivitiesCount(initialDfg)
        maxValueWithActivitiesSpecification = self.sumActivitiesCount(initialDfg, activities)

        condition1 = sumStartActivitiesCount > 0 and maxValueWithActivitiesSpecification < sumStartActivitiesCount
        condition2 = endActivitiesCount > 0 and maxValueWithActivitiesSpecification < endActivitiesCount
        condition3 = sumStartActivitiesCount <= 0 and endActivitiesCount <= 0 and maxValue > 0 and maxValueWithActivitiesSpecification < maxValue
        condition = condition1 or condition2 or condition3

        if condition:
            return True

        return False

    def form_petrinet(self, net, initial_marking, final_marking, must_add_initial_place=False, must_add_final_place=False, initial_connect_to=None, final_connect_to=None, must_add_skip=False, must_add_loop=False):
        """
        Form a Petri net from the current tree structure

        Parameters
        -----------
        net
            Petri net object
        initial_marking
            Initial marking object
        final_marking
            Final marking object
        must_add_initial_place
            When recursive calls are done, tells to add a new place (from which the subtree starts)
        must_add_final_place
            When recursive calls are done, tells to add a new place (into which the subtree goes)
        initial_connect_to
            Initial element (place/transition) to which we should connect the subtree
        final_connect_to
            Final element (place/transition) to which we should connect the subtree
        must_add_skip
            Must add skip transition
        must_add_loop
            Must add loop transition

        Returns
        ----------
        net
            Petri net object
        initial_marking
            Initial marking object
        final_marking
            Final marking object
        lastAddedPlace
            lastAddedPlace
        """
        #print(self.recDepth, self.attributes, self.detectedCut)
        lastAddedPlace = None
        initialPlace = None
        finalPlace = None
        if self.recDepth == 0:
            source = self.get_new_place()
            initial_connect_to = source
            initialPlace = source
            net.places.add(source)
            sink = self.get_new_place()
            final_connect_to = sink
            net.places.add(sink)
            lastAddedPlace = sink
        elif self.recDepth > 0:
            if must_add_initial_place or type(initial_connect_to) is PetriNet.Transition:
                initialPlace = self.get_new_place()
                net.places.add(initialPlace)
                petri.utils.add_arc_from_to(initial_connect_to, initialPlace, net)
            else:
                initialPlace = initial_connect_to
            if must_add_final_place or type(final_connect_to) is PetriNet.Transition:
                finalPlace = self.get_new_place()
                net.places.add(finalPlace)
                petri.utils.add_arc_from_to(finalPlace, final_connect_to, net)
            else:
                finalPlace = final_connect_to
            if self.counts.noOfPlaces == 2 and len(self.activities) > 1:
                initialTrans = self.get_new_hidden_trans(type="tau")
                net.transitions.add(initialTrans)
                newPlace = self.get_new_place()
                net.places.add(newPlace)
                petri.utils.add_arc_from_to(initial_connect_to, initialTrans, net)
                petri.utils.add_arc_from_to(initialTrans, newPlace, net)
                initialPlace = newPlace

        if self.detectedCut == "base_concurrent" or self.detectedCut == "flower":
            if final_connect_to is None or type(final_connect_to) is PetriNet.Transition:
                if finalPlace is not None:
                    lastAddedPlace = finalPlace
                else:
                    lastAddedPlace = self.get_new_place()
                    net.places.add(lastAddedPlace)
            else:
                lastAddedPlace = final_connect_to

            prevNoOfVisibleTransitions = self.counts.noOfVisibleTransitions

            for act in self.activities:
                trans = self.get_transition(act)
                net.transitions.add(trans)
                petri.utils.add_arc_from_to(initialPlace, trans, net)
                petri.utils.add_arc_from_to(trans, lastAddedPlace, net)

            maxValue = self.getMaxValue(self.initialDfg)
            sumStartActivitiesCount = self.getSumStartActivitiesCount(self.initialDfg)
            endActivitiesCount = self.getSumEndActivitiesCount(self.initialDfg)
            maxValueWithActivitiesSpecification = self.sumActivitiesCount(self.initialDfg, self.activities)

            condition1 = sumStartActivitiesCount > 0 and maxValueWithActivitiesSpecification < sumStartActivitiesCount
            condition2 = endActivitiesCount > 0 and maxValueWithActivitiesSpecification < endActivitiesCount
            condition3 = sumStartActivitiesCount <= 0 and endActivitiesCount <= 0 and maxValue > 0 and maxValueWithActivitiesSpecification < maxValue
            condition = condition1 or condition2 or condition3

            if condition and not initial_connect_to.name == "p_1" and prevNoOfVisibleTransitions > 0:
                # add skip transition
                skipTrans = self.get_new_hidden_trans(type="skip")
                net.transitions.add(skipTrans)
                petri.utils.add_arc_from_to(initialPlace, skipTrans, net)
                petri.utils.add_arc_from_to(skipTrans, lastAddedPlace, net)

        # iterate over childs
        if self.detectedCut == "sequential" or self.detectedCut == "loopCut":

            mAddSkip = False
            mAddLoop = False
            if self.detectedCut == "loopCut":
                mAddSkip = True
                mAddLoop = True

            net, initial_marking, final_marking, lastAddedPlace = self.children[0].form_petrinet(net, initial_marking,
                                                                                      final_marking,
                                                                                      initial_connect_to=initialPlace, must_add_skip=self.verify_skip_transition_necessity(mAddSkip, self.initialDfg, self.dfg, self.children[0].dfg, self.activities, self.children[0].activities, initialPlace), must_add_loop=mAddLoop)
            net, initial_marking, final_marking, lastAddedPlace = self.children[1].form_petrinet(net, initial_marking,
                                                                                      final_marking,
                                                                                        initial_connect_to=lastAddedPlace,
                                                                                      final_connect_to=finalPlace, must_add_skip=self.verify_skip_transition_necessity(mAddSkip, self.initialDfg, self.dfg, self.children[1].dfg, self.activities, self.children[1].activities, lastAddedPlace), must_add_loop=mAddLoop)
        elif self.detectedCut == "parallel":
            mAddSkip = False
            mAddLoop = False

            if finalPlace is None:
                finalPlace = self.get_new_place()
                net.places.add(finalPlace)

            children_occurrences = []
            for child in self.children:
                child_occ = self.getMaxValueWithActivitiesSpecification(self.dfg, child.activities)
                children_occurrences.append(child_occ)
            if children_occurrences:
                if not(children_occurrences[0] == children_occurrences[-1]):
                    mAddSkip = True

            parallelSplit = self.get_new_hidden_trans("tauSplit")
            net.transitions.add(parallelSplit)
            petri.utils.add_arc_from_to(initialPlace, parallelSplit, net)

            parallelJoin = self.get_new_hidden_trans("tauJoin")
            net.transitions.add(parallelJoin)
            petri.utils.add_arc_from_to(parallelJoin, finalPlace, net)

            for child in self.children:
                mAddSkipFinal = self.verify_skip_transition_necessity(mAddSkip, self.dfg, self.dfg, child.dfg, self.activities, child.activities, parallelSplit)

                net, initial_marking, final_marking, lastAddedPlace = child.form_petrinet(net, initial_marking,
                                                                                          final_marking,
                                                                                        must_add_initial_place=True, must_add_final_place=True,
                                                                                          initial_connect_to=parallelSplit, final_connect_to=parallelJoin, must_add_skip=mAddSkipFinal, must_add_loop=mAddLoop)

            lastAddedPlace = finalPlace

        elif self.detectedCut == "concurrent":
            mAddSkip = False
            mAddLoop = False

            if finalPlace is None:
                finalPlace = self.get_new_place()
                net.places.add(finalPlace)


            for child in self.children:
                net, initial_marking, final_marking, lastAddedPlace = child.form_petrinet(net, initial_marking,
                                                                                          final_marking,
                                                                                          initial_connect_to=initialPlace, final_connect_to=finalPlace, must_add_skip=self.verify_skip_transition_necessity(mAddSkip, self.initialDfg, self.dfg, child.dfg, self.activities, child.activities, initialPlace), must_add_loop=mAddLoop)

            lastAddedPlace = finalPlace

        if self.detectedCut == "flower" or self.detectedCut == "sequential" or self.detectedCut == "loopCut" or self.detectedCut == "base_concurrent" or self.detectedCut == "parallel" or self.detectedCut == "concurrent":
            if must_add_skip:
                if not (initialPlace.name in self.counts.dictSkips and lastAddedPlace.name in self.counts.dictSkips[initialPlace.name]):
                    skipTrans = self.get_new_hidden_trans(type="skip")
                    net.transitions.add(skipTrans)
                    petri.utils.add_arc_from_to(initialPlace, skipTrans, net)
                    petri.utils.add_arc_from_to(skipTrans, lastAddedPlace, net)

                    if not initialPlace.name in self.counts.dictSkips:
                        self.counts.dictSkips[initialPlace.name] = []

                    self.counts.dictSkips[initialPlace.name].append(lastAddedPlace.name)


            if self.detectedCut == "flower" or must_add_loop:
                if not (initialPlace.name in self.counts.dictLoops and lastAddedPlace.name in self.counts.dictLoops[initialPlace.name]):
                    loopTrans = self.get_new_hidden_trans(type="loop")
                    net.transitions.add(loopTrans)
                    petri.utils.add_arc_from_to(lastAddedPlace, loopTrans, net)
                    petri.utils.add_arc_from_to(loopTrans, initialPlace, net)

                    if not initialPlace.name in self.counts.dictLoops:
                        self.counts.dictLoops[initialPlace.name] = []

                    self.counts.dictLoops[initialPlace.name].append(lastAddedPlace.name)

        if self.recDepth == 0:
            if len(sink.out_arcs) == 0 and len(sink.in_arcs) == 0:
                net.places.remove(sink)
                sink = lastAddedPlace

            if len(sink.out_arcs) > 0:
                newSink = self.get_new_place()
                net.places.add(newSink)
                newHidden = self.get_new_hidden_trans(type="tau")
                net.transitions.add(newHidden)
                petri.utils.add_arc_from_to(sink, newHidden, net)
                petri.utils.add_arc_from_to(newHidden, newSink, net)
                sink = newSink

            if len(source.in_arcs) > 0:
                newSource = self.get_new_place()
                net.places.add(newSource)
                newHidden = self.get_new_hidden_trans(type="tau")
                net.transitions.add(newHidden)
                petri.utils.add_arc_from_to(newSource, newHidden, net)
                petri.utils.add_arc_from_to(newHidden, source, net)
                source = newSource

            source.name = "source"
            sink.name = "sink"
            initial_marking[source] = 1
            final_marking[sink] = 1

        return net, initial_marking, final_marking, lastAddedPlace

class InductMinDirFollows(object):
    def apply(self, trace_log, parameters, activity_key="concept:name"):
        """
        Apply the IMDF algorithm to a log

        Parameters
        -----------
        trace_log
            Trace log
        parameters
            Parameters of the algorithm
        activity_key
            Attribute corresponding to the activity

        Returns
        -----------
        net
            Petri net
        initial_marking
            Initial marking
        final_marking
            Final marking
        """
        self.trace_log = trace_log
        labels = tl_util.get_event_labels(trace_log, activity_key)
        dfg = [(k, v) for k, v in dfg_inst.apply(trace_log, parameters={pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if v > 0]
        return self.apply_dfg(dfg, parameters)

    def apply_dfg(self, dfg, parameters, activity_key="concept:name"):
        """
        Apply the IMDF algorithm to a DFG graph

        Parameters
        -----------
        dfg
            Directly-Follows graph
        parameters
            Parameters of the algorithm

        Returns
        -----------
        net
            Petri net
        initial_marking
            Initial marking
        final_marking
            Final marking
        """

        if parameters is None:
            parameters = {}

        noiseThreshold = 0.0

        if "noiseThreshold" in parameters:
            noiseThreshold = parameters["noiseThreshold"]

        if type(dfg) is Counter or type(dfg) is dict:
            newdfg = []
            for key in dfg:
                value = dfg[key]
                newdfg.append((key, value))
            dfg = newdfg

        c = Counts()
        s = Subtree(dfg, dfg, None, c, 0, noiseThreshold=noiseThreshold)
        net = petri.petrinet.PetriNet('imdf_net_' + str(time.time()))
        initial_marking = Marking()
        final_marking = Marking()
        net, initial_marking, final_marking, lastAddedPlace = s.form_petrinet(net, initial_marking, final_marking)

        return net, initial_marking, final_marking
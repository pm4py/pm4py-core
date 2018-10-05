from copy import copy
from pm4py.algo.discovery.dfg.utils.dfg_utils import get_ingoing_edges, get_outgoing_edges, get_activities_from_dfg
from pm4py.algo.filtering.dfg.dfg_filtering import clean_dfg_based_on_noise_thresh
from pm4py.algo.discovery.inductive.util import shared_constants
from pm4py.algo.discovery.dfg.utils.dfg_utils import filter_dfg_on_act

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
            if not (el[0][1] in self.outgoing and el[0][0] in self.outgoing[el[0][1]]):
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
            dependency = (outgoing - ingoing) / (ingoing + outgoing + 1)
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
            if not (self.activitiesDirlist[0][0] in self.ingoing and self.activitiesDirlist[-1][0] in self.ingoing[
                self.activitiesDirlist[0][0]]):
                set2.add(self.activitiesDirlist[-1][0])
            else:
                return [False, [], []]
        i = 1
        while i < len(self.activitiesDirlist) - 1:
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
                        if not ((act1 in self.outgoing and act2 in self.outgoing[act1]) and (
                                act1 in self.ingoing and act2 in self.ingoing[act1])):
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

        if len(self.activitiesDirlist) > 1:
            set1 = set()
            set2 = set()

            if self.activitiesDirlist[0][1] > shared_constants.LOOP_CONST_1:
                if self.activitiesDirlist[0][0] in self.ingoing:
                    activInput = list(self.ingoing[self.activitiesDirlist[0][0]])
                    for act in activInput:
                        if not act == self.activitiesDirlist[0][0] and self.activitiesDirection[
                            act] < shared_constants.LOOP_CONST_2:
                            set2.add(act)

            if self.activitiesDirlist[-1][1] < shared_constants.LOOP_CONST_4:
                set2.add(self.activitiesDirlist[-1][0])

            if len(set2) > 0:
                for act in self.activities:
                    if not act in set2 or act in set1:
                        if self.activitiesDirection[act] < shared_constants.LOOP_CONST_3:
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
                idx_max_sum = len(sums) - 1

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
                    newDfg = filter_dfg_on_act(self.dfg, comp)
                    self.detectedCut = "parallel"
                    self.children.append(Subtree(newDfg, self.initialDfg, comp, self.counts, self.recDepth + 1,
                                                 noiseThreshold=self.noiseThreshold))
            else:
                if concCut[0]:
                    for comp in concCut[1]:
                        newDfg = filter_dfg_on_act(self.dfg, comp)
                        self.detectedCut = "concurrent"
                        self.children.append(Subtree(newDfg, self.initialDfg, comp, self.counts, self.recDepth + 1,
                                                     noiseThreshold=self.noiseThreshold))
                else:
                    if seqCut[0]:
                        dfg1 = filter_dfg_on_act(self.dfg, seqCut[1])
                        dfg2 = filter_dfg_on_act(self.dfg, seqCut[2])
                        self.detectedCut = "sequential"
                        self.children.append(Subtree(dfg1, self.initialDfg, seqCut[1], self.counts, self.recDepth + 1,
                                                     noiseThreshold=self.noiseThreshold))
                        self.children.append(Subtree(dfg2, self.initialDfg, seqCut[2], self.counts, self.recDepth + 1,
                                                     noiseThreshold=self.noiseThreshold))
                    else:
                        if loopCut[0]:
                            dfg1 = filter_dfg_on_act(self.dfg, loopCut[1])
                            dfg2 = filter_dfg_on_act(self.dfg, loopCut[2])
                            self.detectedCut = "loopCut"
                            self.children.append(
                                Subtree(dfg1, self.initialDfg, loopCut[1], self.counts, self.recDepth + 1,
                                        noiseThreshold=self.noiseThreshold))
                            self.children.append(
                                Subtree(dfg2, self.initialDfg, loopCut[2], self.counts, self.recDepth + 1,
                                        noiseThreshold=self.noiseThreshold))
                        else:
                            if self.noiseThreshold > 0:
                                if not secondIteration:
                                    self.initialize_tree(self.dfg, self.initialDfg, None, secondIteration=True)
                            else:
                                pass
                            self.detectedCut = "flower"
        else:
            self.detectedCut = "base_concurrent"
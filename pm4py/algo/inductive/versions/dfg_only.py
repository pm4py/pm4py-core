from pm4py.log.util import trace_log as tl_util
from pm4py.algo.dfg.verions import native as dfg_inst
from pm4py.algo.inductive.data_structures.dfg_graph import DfgGraph as DfgGraph
from pm4py.models import petri
from pm4py.models.petri.net import Marking
from pm4py.algo.tokenreplay.token_replay import NoConceptNameException
from pm4py.algo.tokenreplay import token_replay
from collections import Counter

import time
from copy import deepcopy, copy
import math


def apply(trace_log, parameters, activity_key='concept:name'):
    indMinDirFollows = InductMinDirFollows()
    return indMinDirFollows.apply(trace_log, parameters, activity_key=activity_key)


class InductMinDirFollows(object):
    def __init__(self):
        """
        Constructor
        """
        self.trace_log = None
        self.addedGraphs = []
        self.startActivitiesInLog = Counter()
        self.activitiesCountInLog = Counter()
        self.maxNoOfActivitiesPerTrace = {}
        self.minNoOfActivitiesPerTrace = {}
        self.addedGraphsActivitiesAvg = []
        self.addedGraphsActivitiesSum = []
        self.noOfPlacesAdded = 0
        self.noOfTransitionsAdded = 0
        self.noOfHiddenTransAdded = 0
        self.noOfHiddenTransAddedSkip = 0
        self.noOfHiddenTransAddedLoop = 0
        self.noOfHiddenTransAddedTau = 0
        self.lastEndSubtreePlaceAdded = []
        self.transitionsMap = {}
        self.addedArcsObjLabels = []
        self.lastPlaceAdded = None

    def apply(self, trace_log, parameters, activity_key='concept:name'):
        """
        Apply the Inductive Miner directly follows algorithm.

        Parameters
        ----------
        trace_log : :class:`pm4py.log.instance.TraceLog`
            Event log to use in the alpha miner, note that it should be a TraceLog!
        activity_key : `str`, optional
            Key to use within events to identify the underlying activity.
            By deafult, the value 'concept:name' is used.
        cleanNetByTokenReplay
            Clean resulting Petri net transitions by using Token Replay

        Returns
        -------
        net : :class:`pm4py.models.petri.instance.PetriNet`
            A Petri net describing the event log that is provided as an input

        References
        ----------
        Leemans, S. J., Fahland, D., & van der Aalst, W. M. (2015, June). Scalable process discovery with guarantees. In International Conference on Enterprise, Business-Process and Information Systems Modeling (pp. 85-101). Springer, Cham.
        """

        self.trace_log = trace_log
        labels = tl_util.get_event_labels(trace_log, activity_key)
        for trace in trace_log:
            if len(trace) > 0:
                traceCounter = Counter()
                if not activity_key in trace[0]:
                    raise NoConceptNameException("at least an event is without "+activity_key)
                self.startActivitiesInLog[trace[0][activity_key]] += 1
                for event in trace:
                    if not activity_key in event:
                        raise NoConceptNameException("at least an event is without "+activity_key)
                    activity = event[activity_key]
                    self.activitiesCountInLog[activity] += 1
                    traceCounter[activity] += 1
                for activity in traceCounter:
                    if not activity in self.maxNoOfActivitiesPerTrace or self.maxNoOfActivitiesPerTrace[activity] < \
                            traceCounter[activity]:
                        self.maxNoOfActivitiesPerTrace[activity] = traceCounter[activity]
                    if not activity in self.minNoOfActivitiesPerTrace or self.minNoOfActivitiesPerTrace[activity] > \
                            traceCounter[activity]:
                        self.minNoOfActivitiesPerTrace[activity] = traceCounter[activity]
                for activity in self.minNoOfActivitiesPerTrace:
                    if not activity in traceCounter:
                        self.minNoOfActivitiesPerTrace[activity] = 0

        self.dfg = [(k, v) for k, v in dfg_inst.compute_dfg(trace_log, activity_key).items() if v > 0]
        self.dfg = sorted(self.dfg, key=lambda x: x[1], reverse=True)
        pairs = [k[0] for k in self.dfg]
        labels = [str(x) for x in labels]
        pairs = [(str(x[0]), str(x[1])) for x in pairs]
        net = petri.net.PetriNet('imdf_net_' + str(time.time()))
        start = petri.net.PetriNet.Place('p_' + str(self.noOfPlacesAdded))
        net.places.add(start)
        self.lastEndSubtreePlaceAdded = [start]
        if len(self.startActivitiesInLog.keys()) > 1:
            self.noOfHiddenTransAdded = self.noOfHiddenTransAdded + 1
            self.noOfHiddenTransAddedSkip = self.noOfHiddenTransAddedSkip + 1
            hiddenTransSkipStartMult = petri.net.PetriNet.Transition('iskip_' + str(self.noOfHiddenTransAdded), None)
            net.transitions.add(hiddenTransSkipStartMult)
            self.noOfPlacesAdded = self.noOfPlacesAdded + 1
            newPlace = petri.net.PetriNet.Place('p_' + str(self.noOfPlacesAdded))
            net.places.add(newPlace)
            petri.utils.add_arc_from_to(start, hiddenTransSkipStartMult, net)
            petri.utils.add_arc_from_to(hiddenTransSkipStartMult, newPlace, net)
            self.lastEndSubtreePlaceAdded = [newPlace]
            self.addedGraphs.append([])
            self.addedGraphsActivitiesAvg.append(len(trace_log))
            self.addedGraphsActivitiesSum.append(len(trace_log))
        net = self.recFindCut(net, labels, pairs, 0, self.lastEndSubtreePlaceAdded)
        # check the final marking
        final_marking = petri.net.Marking()
        for p in net.places:
            if not p.out_arcs:
                final_marking[p] = 1
        if len(final_marking) == 0:
            self.noOfHiddenTransAdded = self.noOfHiddenTransAdded + 1
            self.noOfHiddenTransAddedTau = self.noOfHiddenTransAddedTau + 1
            hiddenTransEnd = petri.net.PetriNet.Transition('tau_' + str(self.noOfHiddenTransAdded), None)
            end = petri.net.PetriNet.Place('end')
            net.places.add(end)
            net.transitions.add(hiddenTransEnd)
            petri.utils.add_arc_from_to(self.lastPlaceAdded, hiddenTransEnd, net)
            petri.utils.add_arc_from_to(hiddenTransEnd, end, net)
        elif len(final_marking) == 1:
            for p in final_marking:
                p.name = "end"
        # self.lastPlaceAdded.name = "end"
        # check the initial marking
        initial_marking = petri.net.Marking()
        for p in net.places:
            if not p.in_arcs:
                initial_marking[p] = 1
        if len(initial_marking) == 0:
            self.noOfHiddenTransAdded = self.noOfHiddenTransAdded + 1
            self.noOfHiddenTransAddedTau = self.noOfHiddenTransAddedTau + 1
            hiddenTransStart = petri.net.PetriNet.Transition('tau_' + str(self.noOfHiddenTransAdded), None)
            newStart = petri.net.PetriNet.Place('start')
            net.places.add(newStart)
            net.transitions.add(hiddenTransStart)
            petri.utils.add_arc_from_to(newStart, hiddenTransStart, net)
            petri.utils.add_arc_from_to(hiddenTransStart, start, net)
            start = newStart
        else:
            for p in initial_marking:
                p.name = "start"
                break

        initial_marking = Marking({start: 1})
        final_marking = petri.net.Marking()
        for p in net.places:
            if not p.out_arcs:
                final_marking[p] = 1

        if parameters is not None and "cleanNetByTokenReplay" in parameters and parameters["cleanNetByTokenReplay"]:
            [traceIsFit, traceFitnessValue, activatedTransitions, placeFitnessPerTrace, reachedMarkings, enabledTransitionsInMarkings] = token_replay.apply_log(trace_log, net, initial_marking, final_marking, activity_key=activity_key)
            actiTrans = set()
            for trace in activatedTransitions:
                for trans in trace:
                    actiTrans.add(trans)
            transitions = copy(net.transitions)
            for transition in transitions:
                if not transition in actiTrans:
                    inArcs = copy(transition.in_arcs)
                    for arc in inArcs:
                        transition.in_arcs.remove(arc)
                        net.arcs.remove(arc)
                    outArcs = copy(transition.out_arcs)
                    for arc in outArcs:
                        transition.out_arcs.remove(arc)
                        net.arcs.remove(arc)
                    net.transitions.remove(transition)

        return net, initial_marking

    def calculateActivitiesArcsDirection(self, labels):
        """
        Calculate activities arcs directions
        Values near to 1 indicates that the activities has an high number of outgoing edges
        Values near to -1 indicates that the activities has an high number of ingoing edges

        Parameters
        ----------
        labels
            Activities belonging to the subtree
        """
        activitiesArcsDirections = {}
        activitiesOutgoingEdges = {}
        activitiesIngoingEdges = {}
        for dfgEl in self.dfg:
            dfgAct1 = dfgEl[0][0]
            dfgAct2 = dfgEl[0][1]
            dfgVal = dfgEl[1]

            if dfgAct1 in labels and dfgAct2 in labels:
                if not dfgAct1 in activitiesOutgoingEdges:
                    activitiesOutgoingEdges[dfgAct1] = 0
                if not dfgAct2 in activitiesIngoingEdges:
                    activitiesIngoingEdges[dfgAct2] = 0
                activitiesOutgoingEdges[dfgAct1] = activitiesOutgoingEdges[dfgAct1] + dfgVal
                activitiesIngoingEdges[dfgAct2] = activitiesIngoingEdges[dfgAct2] + dfgVal

        allActivities = set(activitiesIngoingEdges.keys()).union(set(activitiesOutgoingEdges.keys()))

        for act in allActivities:
            if act in activitiesIngoingEdges.keys() and not act in activitiesOutgoingEdges.keys():
                activitiesArcsDirections[act] = -(activitiesIngoingEdges[act])/(activitiesIngoingEdges[act] + 1)
            elif act in activitiesOutgoingEdges.keys() and not act in activitiesIngoingEdges.keys():
                activitiesArcsDirections[act] = activitiesOutgoingEdges[act] / (activitiesOutgoingEdges[act] + 1)
            else:
                activitiesArcsDirections[act] = (activitiesOutgoingEdges[act] - activitiesIngoingEdges[act]) / (activitiesOutgoingEdges[act] + activitiesIngoingEdges[act] + 1)

        return activitiesArcsDirections

    def avgSubtree(self, labels, typ):
        """
        Do the average of activities occurrences in a subtree

        Parameters
        ----------
        labels
            Activities belonging to the subtree
        typ
            Type of subtree that is being added
        """
        avg = 0
        for el in labels:
            if type(el) is list:
                avg = avg + self.avgSubtree(el, "rec")
                avg = float(avg) / float(len(labels))
            else:
                avg = avg + self.activitiesCountInLog[el]

        return avg

    def sumSubtree(self, labels, typ):
        """
        Do the sum of activities occurrences in a subtree

        Parameters
        ----------
        labels
            Activities belonging to the subtree
        typ
            Type of subtree that is being added
        """
        sum = 0
        for el in labels:
            if type(el) is list:
                sum = sum + self.sumSubtree(el, "rec")
            else:
                sum = sum + self.activitiesCountInLog[el]

        return sum

    def verifySubtreeLoopCondition(self, labels):
        ret = False
        for el in labels:
            for subel in el:
                if self.maxNoOfActivitiesPerTrace[subel] > 1:
                    ret = True
                    break
        return ret

    """def verifyNecessityOfSkipTransitionForConcurrentPairs(self, labels):
        ret = False
        for el in labels:
            for subel in el:
                if self.minNoOfActivitiesPerTrace[subel] < 1:
                    ret = True
                    break
        return ret"""

    def hiddenTransitionVisibleLabel(self, name):
        return None

    def addSubtreeToModel(self, net, labels, type, dfgGraph, refToLastPlace, activInSelfLoop,
                          mustAddSkipHiddenTrans=False, mustAddBackwardHiddenTrans=False):
        """
        Adds a part of the tree to the Petri net

        Parameters
        ----------
        net
            Petri net that we are building
        labels
            Labels of the subtree we are adding
        type
            Type of the subtree we are adding (parallel, concurrent, flower)
        dfgGraph
            Directly follows graph object
        refToLastPlace
            Place that we should attach on
        """
        averagedSubtree = self.avgSubtree(labels, type)
        summedSubtree = self.sumSubtree(labels, type)
        self.noOfPlacesAdded = self.noOfPlacesAdded + 1
        subtreeEnd = petri.net.PetriNet.Place('p_' + str(self.noOfPlacesAdded))
        self.lastPlaceAdded = subtreeEnd
        net.places.add(subtreeEnd)
        originalType = deepcopy(type)

        type = deepcopy(originalType)
        condition1 = mustAddSkipHiddenTrans and (len(self.addedGraphsActivitiesSum) > 0 and abs(summedSubtree - max(self.addedGraphsActivitiesSum)) > 0.5)

        # add the hidden transitions that permits to skip the tree
        self.noOfHiddenTransAdded = self.noOfHiddenTransAdded + 1
        self.noOfHiddenTransAddedSkip = self.noOfHiddenTransAddedSkip + 1
        if condition1:
            hiddenTransSkipTree = petri.net.PetriNet.Transition('fskip_' + str(self.noOfHiddenTransAdded),
                                                                self.hiddenTransitionVisibleLabel(
                                                                    'fskip_' + str(self.noOfHiddenTransAdded)))
        else:
            hiddenTransSkipTree = petri.net.PetriNet.Transition('skip_' + str(self.noOfHiddenTransAdded),
                                                                self.hiddenTransitionVisibleLabel(
                                                                    'skip_' + str(self.noOfHiddenTransAdded)))
        net.transitions.add(hiddenTransSkipTree)
        petri.utils.add_arc_from_to(refToLastPlace[0], hiddenTransSkipTree, net)
        petri.utils.add_arc_from_to(hiddenTransSkipTree, subtreeEnd, net)

        type = deepcopy(originalType)

        # here we must add also the coming back arc
        self.noOfHiddenTransAdded = self.noOfHiddenTransAdded + 1
        self.noOfHiddenTransAddedLoop = self.noOfHiddenTransAddedLoop + 1
        hiddenTransLoop = petri.net.PetriNet.Transition('loop_' + str(self.noOfHiddenTransAdded),
                                                        self.hiddenTransitionVisibleLabel(
                                                            'loop_' + str(self.noOfHiddenTransAdded)))
        net.transitions.add(hiddenTransLoop)
        petri.utils.add_arc_from_to(hiddenTransLoop, refToLastPlace[0], net)
        petri.utils.add_arc_from_to(subtreeEnd, hiddenTransLoop, net)

        # each label is a cluster of sequentially followed activities
        for l in labels:
            transitions = []
            i = 0
            while i < len(l):
                li = l[i]
                self.noOfTransitionsAdded = self.noOfTransitionsAdded + 1
                transLab = li
                # add the transitions to the model if needed
                if not transLab in self.transitionsMap:
                    transObj = petri.net.PetriNet.Transition('t_' + str(self.noOfTransitionsAdded), li)
                    transitions.append(transObj)
                    self.transitionsMap[transLab] = transObj
                    net.transitions.add(transitions[-1])
                else:
                    transitions.append(self.transitionsMap[transLab])
                # input element of the sequence cluster
                if i == 0:
                    if type == "concurrent" or type == "flower":
                        # if we are adding a concurrent or flower subtree, then we have no worries:
                        # we need to add an arc between the previous place and the transition
                        arcLabel = str(refToLastPlace[0]) + str(transitions[0])
                        if not arcLabel in self.addedArcsObjLabels:
                            petri.utils.add_arc_from_to(refToLastPlace[0], transitions[0], net)
                            self.addedArcsObjLabels.append(arcLabel)
                if i > 0:
                    # we add sequential elements inside the cluster
                    if not transitions[-2].label == transitions[-1].label:
                        arcLabel = str(transitions[-2]) + str(transitions[-1])
                        if not arcLabel in self.addedArcsObjLabels:
                            self.noOfPlacesAdded = self.noOfPlacesAdded + 1
                            auxiliaryPlace = petri.net.PetriNet.Place('p_' + str(self.noOfPlacesAdded))
                            net.places.add(auxiliaryPlace)
                            petri.utils.add_arc_from_to(transitions[-2], auxiliaryPlace, net)
                            petri.utils.add_arc_from_to(auxiliaryPlace, transitions[-1], net)
                            self.addedArcsObjLabels.append(arcLabel)
                if i == len(l) - 1:
                    if type == "concurrent" or type == "flower":
                        # if we are adding a concurrent or flower subtree, then we have no worries:
                        # we need to add an arc between the transition and the end-subtree place
                        arcLabel = str(transitions[-1]) + str(subtreeEnd)
                        if not arcLabel in self.addedArcsObjLabels:
                            petri.utils.add_arc_from_to(transitions[-1], subtreeEnd, net)
                            self.addedArcsObjLabels.append(arcLabel)
                i = i + 1
        refToLastPlace[0] = subtreeEnd
        self.addedGraphs.append(labels)
        self.addedGraphsActivitiesAvg.append(averagedSubtree)
        self.addedGraphsActivitiesSum.append(summedSubtree)

        return net

    def addConnectionPlace(self, net, newRefToLastPlace, inputConnectionPlace=None):
        """
        Creates a connection place that merges concurrent connected subgraphs
        through the use of hidden transitions

        Parameters
        ----------
        net
            Petri net
        newRefToLastPlace
            Last place of the connected subgraph subtree
        inputConnectionPlace
            Connection place if already added to the model
            (serves for the connection of all the connected subgraphs)
        """

        if inputConnectionPlace is None:
            self.noOfPlacesAdded = self.noOfPlacesAdded + 1
            connectionPlace = petri.net.PetriNet.Place('p_' + str(self.noOfPlacesAdded))
            self.lastPlaceAdded = connectionPlace
            net.places.add(connectionPlace)
        else:
            connectionPlace = inputConnectionPlace
        self.noOfHiddenTransAdded = self.noOfHiddenTransAdded + 1
        self.noOfHiddenTransAddedTau = self.noOfHiddenTransAddedTau + 1
        hiddenTransition = petri.net.PetriNet.Transition('tau_' + str(self.noOfHiddenTransAdded),
                                                         self.hiddenTransitionVisibleLabel(
                                                             'tau_' + str(self.noOfHiddenTransAdded)))
        net.transitions.add(hiddenTransition)
        petri.utils.add_arc_from_to(newRefToLastPlace[0], hiddenTransition, net)
        petri.utils.add_arc_from_to(hiddenTransition, connectionPlace, net)

        return [net, connectionPlace, hiddenTransition]

    def addConnectionPlaceParallel(self, net, newRefToLastPlace, inputConnectionPlace=None, inputHiddenTransition=None):
        """
        Create a merge of parallel connected subgraphs
        through the use of hidden transitions

        Parameters
        ----------
        net
            Petri net
        newRefToLastPlace
            Referrence to the last added place previously
        inputConnectionPlace
            (if already added) connection place at the end of subtree
        inputHiddenTransition
            (if already added) connection transition at the end of subtree
        """
        if inputConnectionPlace is None:
            self.noOfPlacesAdded = self.noOfPlacesAdded + 1
            connectionPlace = petri.net.PetriNet.Place('p_' + str(self.noOfPlacesAdded))
            self.lastPlaceAdded = connectionPlace
            net.places.add(connectionPlace)
        else:
            connectionPlace = inputConnectionPlace

        if inputHiddenTransition is None:
            self.noOfHiddenTransAdded = self.noOfHiddenTransAdded + 1
            self.noOfHiddenTransAddedTau = self.noOfHiddenTransAddedTau + 1
            hiddenTransition = petri.net.PetriNet.Transition('tau_' + str(self.noOfHiddenTransAdded),
                                                             self.hiddenTransitionVisibleLabel(
                                                                 'tau_' + str(self.noOfHiddenTransAdded)))
            net.transitions.add(hiddenTransition)
            petri.utils.add_arc_from_to(hiddenTransition, connectionPlace, net)
        else:
            hiddenTransition = inputHiddenTransition
        petri.utils.add_arc_from_to(newRefToLastPlace[0], hiddenTransition, net)
        return [net, connectionPlace, hiddenTransition]

    def getActivitiesInSelfLoop(self, origPairs):
        """
        Get activities that are in self loop

        Parameters
        ----------
        origPairs
            Original pairs
        """
        activInSelfLoop = []
        for p in origPairs:
            if p[0] == p[1]:
                activInSelfLoop.append(p[0])

        return activInSelfLoop

    def checkAverage(self, negatedConnectedComponents):
        """
        Check average activity occurrence in a subtree

        Parameters
        ----------
        negatedConnectedComponents
            Negated connected components
        """
        if type(negatedConnectedComponents) is list and type(negatedConnectedComponents[0]) is list:
            actiCount = []
            for x in negatedConnectedComponents:
                actiCount.append({})
                for y in x:
                    actiCount[-1][y] = self.activitiesCountInLog[y]
            averages = sorted([self.avgSubtree(x, "concurrent") for x in negatedConnectedComponents])
            if abs(averages[-1] - averages[0]) > 0.5:
                return False
        return True

    def checkParallelCutCouple(self, firstNegatedComponent, secondNegatedComponent, origPairs):
        """
        Check parallel cut couple

        Parameters
        ----------
        firstNegatedComponent
            First negated component
        secondNegatedComponent
            Second negated component
        originalPairs
            Original pairs of activities
        """
        z = 0
        while z < len(firstNegatedComponent):
            k = 0
            while k < len(secondNegatedComponent):
                pair1ToCheck = (firstNegatedComponent[z], secondNegatedComponent[k])
                pair1CheckResult = pair1ToCheck in origPairs
                pair2ToCheck = (secondNegatedComponent[k], firstNegatedComponent[z])
                pair2CheckResult = pair2ToCheck in origPairs
                pairCheckResult = (pair1CheckResult and pair2CheckResult)
                if not pairCheckResult:
                    return False
                else:
                    pass
                k = k + 1
            z = z + 1
        return True

    def checkParallelCut(self, negatedConnectedComponents, origPairs):
        """
        Check parallel cut

        Parameters
        ----------
        negatedConnectedComponents
            Negated connected components
        origPairs
            Original pairs of activities
        """
        origNegatedConnectedComponents = copy(negatedConnectedComponents)

        i = 0
        while i < len(negatedConnectedComponents):
            mustContinue = False
            j = i + 1
            while j < len(negatedConnectedComponents):
                result = self.checkParallelCutCouple(negatedConnectedComponents[i], negatedConnectedComponents[j], origPairs)
                #print("result = ",result)
                if not result:
                    #print("merging i=",i,"j=",j)
                    negatedConnectedComponents[i] = negatedConnectedComponents[i] + copy(negatedConnectedComponents[j])
                    del negatedConnectedComponents[j]
                    mustContinue = True
                    continue
                j = j + 1
            if mustContinue:
                continue
            i = i + 1

        return negatedConnectedComponents

    def calculateEntropy(self, sets):
        """
        Calculate entropy over a list of lists of activities

        Parameters
        ----------
        sets
            List of lists of activities
        """
        entropy = 0.0
        sum = 0.0
        for set in sets:
            sum = sum + len(set)
        for set in sets:
            p = len(set) / sum
            entropy = entropy - p * math.log(p)/math.log(2)
        return entropy

    def giveScoreToConcurrentCut(self, connectedComponents):
        """
        Give score to a concurrent cut

        Parameters
        ----------
        connectedComponents
            Connected components
        """
        return 0.8 * self.calculateEntropy(connectedComponents)

    def giveScoreToParallelCut(self, connectedComponents):
        """
        Give score to a parallel cut

        Parameters
        ----------
        connectedComponents
            Connected components
        """
        return 0.8 * self.calculateEntropy(connectedComponents)

    def giveScoreToLoopCut(self, loopCut):
        """
        Give score to a parallel cut

        Parameters
        ----------
        loopCut
            Loop cut
        """
        sets = copy(loopCut)
        del sets[0]
        return 0.25 * self.calculateEntropy(sets)

    def recFindCut(self, net, nodesLabels, pairs, recDepth, refToLastPlace, mustAddSkipHiddenTrans=False,
                   mustAddBackwardHiddenTrans=False, callerSpecification=None):
        """
        Apply the algorithm recursively discovering connected components and maximal cuts

        Parameters
        ----------
        net
            Petri net
        nodesLabels
            Labels belonging to the subtree we are recurring on
        pairs
            Pairs belonging to the subtree we are recurring on
        recDepth
            Depth of the recursion we have reached
        refToLastPlace
            Place that we should attach the subtree
        """
        dfgGraph = DfgGraph(nodesLabels, pairs)
        dfgGraph = dfgGraph.formGroupedGraph()
        pairs = dfgGraph.getPairs()
        origPairs = dfgGraph.getOrigPairs()
        origLabels = dfgGraph.getOrigLabels()
        activitiesArcsDirection = self.calculateActivitiesArcsDirection(origLabels)
        activInSelfLoop = self.getActivitiesInSelfLoop(origPairs)
        connectedComponents = dfgGraph.findConnectedComponents()
        # negate the graph to observe parallel behavior
        negatedGraph = deepcopy(dfgGraph)
        negatedGraph.negate()
        negatedPairs = negatedGraph.getPairs()
        negatedOrigPairs = negatedGraph.origPairs
        negatedConnectedComponents = negatedGraph.findConnectedComponents()
        parallelCutMayBePresent = len(negatedConnectedComponents) > 1 and len(connectedComponents) == 1
        if parallelCutMayBePresent:
            negatedConnectedComponents = self.checkParallelCut(negatedConnectedComponents, origPairs)
            parallelCutMayBePresent = len(negatedConnectedComponents) > 1 and len(connectedComponents) == 1
        maximumCut = None
        loopCut = None
        if True:
            maximumCut = dfgGraph.findMaximumCut(self.addedGraphs, activitiesArcsDirection=activitiesArcsDirection)
            # check if the cut is plausible
            if not (maximumCut[0] and maximumCut[1] and maximumCut[2]):
                maximumCut = None
        if maximumCut is None:
            loopCut = dfgGraph.findLoopCut(activitiesArcsDirection)
            # check if the cut is plausible
            if not (loopCut[0] and loopCut[1] and loopCut[2]):
                loopCut = None

        if len(pairs) == 0:
            summedSubtree = self.sumSubtree(list(dfgGraph.labelsCorresp.values()), type)
            conditionSkipPairs = len(self.addedGraphsActivitiesSum) > 0 and\
                                  (abs(summedSubtree - max(self.addedGraphsActivitiesSum)) > 0.5)


            oldRefToLastPlace = [copy(refToLastPlace)[0]]
            oldNumberOfHiddenTransitionsSkip = copy(self.noOfHiddenTransAddedSkip)
            oldSummedSubtree = 0
            if self.addedGraphsActivitiesSum:
                oldSummedSubtree = self.addedGraphsActivitiesSum[-1]
            # we have all unconnected activities / clusters of sequential activities: add them to the model!
            net = self.addSubtreeToModel(net, list(dfgGraph.labelsCorresp.values()), "concurrent", dfgGraph,
                                         refToLastPlace, activInSelfLoop, mustAddSkipHiddenTrans=mustAddSkipHiddenTrans,
                                         mustAddBackwardHiddenTrans=mustAddBackwardHiddenTrans)
            newNumberOfHiddenTransitionsSkip = copy(self.noOfHiddenTransAddedSkip)

            if oldNumberOfHiddenTransitionsSkip == newNumberOfHiddenTransitionsSkip:
                self.noOfHiddenTransAddedSkip = self.noOfHiddenTransAddedSkip + 1
                self.noOfHiddenTransAdded = self.noOfHiddenTransAdded + 1
                hiddenTransition = petri.net.PetriNet.Transition('cskip_' + str(self.noOfHiddenTransAdded),
                                                                  self.hiddenTransitionVisibleLabel(
                                                                      'cskip_' + str(self.noOfHiddenTransAdded)))
                net.transitions.add(hiddenTransition)
                petri.utils.add_arc_from_to(oldRefToLastPlace[0], hiddenTransition, net)
                petri.utils.add_arc_from_to(hiddenTransition, refToLastPlace[0], net)
        else:
            possibleOptionsWithScore = []

            if maximumCut is not None:
                possibleOptionsWithScore.append(["maximumCut", 1.0, maximumCut])
            if len(connectedComponents) > 1:
                possibleOptionsWithScore.append(["concurrentCut", self.giveScoreToConcurrentCut(connectedComponents), connectedComponents])
            if parallelCutMayBePresent:
                possibleOptionsWithScore.append(["parallelCut", self.giveScoreToParallelCut(negatedConnectedComponents), negatedConnectedComponents])
            if loopCut is not None:
                possibleOptionsWithScore.append(["loopCut", self.giveScoreToLoopCut(loopCut), loopCut])

            if possibleOptionsWithScore:
                possibleOptionsWithScore = sorted(possibleOptionsWithScore, key=lambda x: x[1], reverse=True)
                bestOptionLabel = possibleOptionsWithScore[0][0]

                if bestOptionLabel == "maximumCut":
                    pairs1 = dfgGraph.projectPairs(maximumCut[1], origPairs)
                    pairs2 = dfgGraph.projectPairs(maximumCut[2], origPairs)
                    net = self.recFindCut(net, maximumCut[1], pairs1, recDepth + 1, refToLastPlace,
                                          mustAddSkipHiddenTrans=mustAddSkipHiddenTrans,
                                          mustAddBackwardHiddenTrans=mustAddBackwardHiddenTrans, callerSpecification="maximumCut")
                    net = self.recFindCut(net, maximumCut[2], pairs2, recDepth + 1, refToLastPlace,
                                          mustAddSkipHiddenTrans=mustAddSkipHiddenTrans,
                                          mustAddBackwardHiddenTrans=mustAddBackwardHiddenTrans, callerSpecification="maximumCut")
                elif bestOptionLabel == "concurrentCut":
                    connectionPlace = None
                    originalRefToLastPlace = [copy(refToLastPlace)[0]]
                    for cc in connectedComponents:
                        # we add the connected component and memorize the connection place
                        ccPairs = dfgGraph.projectPairs(cc, origPairs)
                        newRefToLastPlace = [copy(originalRefToLastPlace)[0]]

                        net = self.recFindCut(net, cc, ccPairs, recDepth + 1, newRefToLastPlace,
                                              mustAddSkipHiddenTrans=mustAddSkipHiddenTrans,
                                              mustAddBackwardHiddenTrans=mustAddBackwardHiddenTrans, callerSpecification="concurrentCut")
                        [net, connectionPlace, connectionTransition] = self.addConnectionPlace(net, newRefToLastPlace,
                                                                                               inputConnectionPlace=connectionPlace)
                    refToLastPlace[0] = connectionPlace
                elif bestOptionLabel == "parallelCut":
                    connectionPlace = None
                    connectionTransition = None

                    self.noOfHiddenTransAddedTau = self.noOfHiddenTransAddedTau + 1
                    self.noOfHiddenTransAdded = self.noOfHiddenTransAdded + 1
                    inputHiddenTransition = petri.net.PetriNet.Transition('tau_' + str(self.noOfHiddenTransAdded),
                                                                          self.hiddenTransitionVisibleLabel(
                                                                              'tau_' + str(self.noOfHiddenTransAdded)))
                    net.transitions.add(inputHiddenTransition)
                    petri.utils.add_arc_from_to(refToLastPlace[0], inputHiddenTransition, net)

                    for cc in negatedConnectedComponents:
                        self.noOfPlacesAdded = self.noOfPlacesAdded + 1
                        inputPlace = petri.net.PetriNet.Place('p_' + str(self.noOfPlacesAdded))
                        net.places.add(inputPlace)
                        newRefToLastPlace = [inputPlace]
                        petri.utils.add_arc_from_to(inputHiddenTransition, inputPlace, net)
                        # we add the connected component and memorize the connection place
                        ccPairs = negatedGraph.projectPairs(cc, origPairs)
                        net = self.recFindCut(net, cc, ccPairs, recDepth + 1, newRefToLastPlace, mustAddSkipHiddenTrans=True,
                                              mustAddBackwardHiddenTrans=True, callerSpecification="parallelCut")
                        [net, connectionPlace, connectionTransition] = self.addConnectionPlaceParallel(net, newRefToLastPlace,
                                                                                                       inputConnectionPlace=connectionPlace,
                                                                                                       inputHiddenTransition=connectionTransition)
                    refToLastPlace[0] = connectionPlace
                elif bestOptionLabel == "loopCut":
                    pairs1 = dfgGraph.projectPairs(loopCut[1], origPairs)
                    pairs2 = dfgGraph.projectPairs(loopCut[2], origPairs)
                    originRefToLastPlace = copy(refToLastPlace)
                    net = self.recFindCut(net, loopCut[1], pairs1, recDepth + 1, refToLastPlace,
                                          mustAddSkipHiddenTrans=True, mustAddBackwardHiddenTrans=True, callerSpecification="loopCut")
                    intermediateRefToLastPlace = copy(refToLastPlace)
                    net = self.recFindCut(net, loopCut[2], pairs2, recDepth + 1, refToLastPlace, mustAddSkipHiddenTrans=True, mustAddBackwardHiddenTrans=True, callerSpecification="loopCut")
                    self.noOfHiddenTransAddedLoop = self.noOfHiddenTransAddedLoop + 1
                    self.noOfHiddenTransAdded = self.noOfHiddenTransAdded + 1
                    loopTransition = petri.net.PetriNet.Transition('lcloop_' + str(self.noOfHiddenTransAdded),
                                                                   self.hiddenTransitionVisibleLabel(
                                                                       'lcloop_' + str(self.noOfHiddenTransAdded)))
                    net.transitions.add(loopTransition)
                    petri.utils.add_arc_from_to(refToLastPlace[0], loopTransition, net)
                    petri.utils.add_arc_from_to(loopTransition, originRefToLastPlace[0], net)
                    self.noOfHiddenTransAddedSkip = self.noOfHiddenTransAddedSkip + 1
                    self.noOfHiddenTransAdded = self.noOfHiddenTransAdded + 1
                    skipTransition = petri.net.PetriNet.Transition('lcskip_' + str(self.noOfHiddenTransAdded),
                                                                   self.hiddenTransitionVisibleLabel(
                                                                       'lcskip_' + str(self.noOfHiddenTransAdded)))
                    net.transitions.add(skipTransition)
                    petri.utils.add_arc_from_to(originRefToLastPlace[0], skipTransition, net)
                    petri.utils.add_arc_from_to(skipTransition, intermediateRefToLastPlace[0], net)
            else:
                # if everything fails, then flower!
                net = self.addSubtreeToModel(net, list(dfgGraph.labelsCorresp.values()), "flower", dfgGraph,
                                             refToLastPlace, activInSelfLoop,
                                             mustAddSkipHiddenTrans=mustAddSkipHiddenTrans,
                                             mustAddBackwardHiddenTrans=mustAddSkipHiddenTrans)
        return net
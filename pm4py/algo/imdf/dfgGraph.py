from copy import copy, deepcopy
import random

HIGH_QUALITY_CUT_CONSTANT = 0.65
LOOP_CONSTANT = 0.2

class CutResultObj(object):
    """ Object useful for the second
    maximal cut detection algorithm """

    def __init__(self):
        """
        Constructor

        """
        self.optimalChoice = deepcopy({})
        self.optimalChoice["set1"] = deepcopy(set())
        self.optimalChoice["set2"] = deepcopy(set())
        self.highQualityCutFound = []
        self.highQualityCutFound.append(False)

    def calculateCutCost(self, choice, pairs):
        """
        Calculates the cost of a cut

        """
        cost = 0
        for p in pairs:
            if p[0] in choice["set1"] and p[1] in choice["set2"]:
                cost = cost + 1
        return cost

    def findMaximumCutAlgo2Rec(self, currentChoice, activities, pairs, nodesInputActivities, nodesOutputActivities,
                               recDepth):
        """
        Recursion algorithm to find an optimal maximal cut

        Parameters
        ----------
        currentChoice
            Current choice of cut (may be partial)
        activities
            Activities that we must find the cut on
        pairs
            Pairs of relations between activities
        nodesInputActivities
            Input activities for nodes according to pairs
        nodesOutputActivities
            Output activities for nodes according to pairs
        recDepth
            Reached recursion level
        """
        if self.highQualityCutFound[0]:
            return True
        if recDepth == len(activities):
            # print(currentChoice["set1"],currentChoice["set2"])
            if len(currentChoice["set1"]) > 0 and len(currentChoice["set2"]) > 0:
                if len(currentChoice["set1"]) > HIGH_QUALITY_CUT_CONSTANT * len(currentChoice["set2"]) and len(
                        currentChoice["set2"]) > HIGH_QUALITY_CUT_CONSTANT * len(currentChoice["set1"]):
                    self.highQualityCutFound[0] = True
                thisCutCost = self.calculateCutCost(currentChoice, pairs)
                optCutCost = self.calculateCutCost(self.optimalChoice, pairs)
                if thisCutCost > optCutCost:
                    # print(str(optCutCost))
                    # print("thisCutCost = ",thisCutCost," optCutCost=",optCutCost,self.optimalChoice,len(currentChoice["set1"]),len(currentChoice["set2"]))
                    self.optimalChoice["set1"] = deepcopy(currentChoice["set1"])
                    self.optimalChoice["set2"] = deepcopy(currentChoice["set2"])
        else:
            thisActivity = activities[recDepth]
            inteWithSet1 = set.intersection(nodesOutputActivities[thisActivity], currentChoice["set1"])
            inteWithSet2 = set.intersection(nodesInputActivities[thisActivity], currentChoice["set2"])

            # print(len(inteWithSet1))
            # print(len(inteWithSet2))
            addActToSet1Result = False
            addActToSet2Result = False
            if len(inteWithSet2) == 0:
                newCurrentChoice = deepcopy(currentChoice)
                newCurrentChoice["set1"].add(thisActivity)
                addActToSet1Result = self.findMaximumCutAlgo2Rec(newCurrentChoice, activities, pairs,
                                                                 nodesInputActivities, nodesOutputActivities,
                                                                 recDepth + 1)
            if len(inteWithSet1) == 0 and not self.highQualityCutFound[0]:
                newCurrentChoice = deepcopy(currentChoice)
                newCurrentChoice["set2"].add(thisActivity)
                addActToSet2Result = self.findMaximumCutAlgo2Rec(newCurrentChoice, activities, pairs,
                                                                 nodesInputActivities, nodesOutputActivities,
                                                                 recDepth + 1)
            if not (addActToSet1Result or addActToSet2Result):
                return False
        return True


class Node(object):
    def __init__(self, label):
        """
        Constructor

        Parameters
        ----------
        label
            Node label
        """
        self.label = label
        self.countConnections = 0
        self.inputNodes = []
        self.outputNodes = []

    def addInputNode(self, node):
        """
        Adds a node that is left-wise connected to this node

        Parameters
        ----------
        node
            Connected node
        """
        self.inputNodes.append(node)
        self.countConnections = self.countConnections + 1

    def addOutputNode(self, node):
        """
        Adds a node that is right-wise connected to this node

        Parameters
        ----------
        node
            Connected node
        """
        self.outputNodes.append(node)
        self.countConnections = self.countConnections + 1

    def __repr__(self):
        return self.label


class DfgGraph(object):
    def __init__(self, nodesLabels, pairs, labelsCorresp=None, invLabelsCorresp=None, origPairs=None, origLabels=None,
                 enableSequenceDetection=False):
        """
        Construct a Directly-follows graph starting from the provision of labels and pairs

        Parameters
        ----------
        nodesLabels
            Labels
        pairs
            Pairs (relationships between activities)
        labelsCorresp
            (if the graph gets clustered) Clusters of sequential activities. For each cluster, we memorize the list of activities belonging to the cluster
        invLabelsCorresp
            (if the graph gets clustered) Clusters of sequential activities. For each activity, we correspond the cluster it belongs to
        origPairs
            (if the graph gets clustered) Relationships pairs in the original non-clustered graph
        origLabels
            (if the graph gets clustered) Labels in the original non-clustered graph
        """
        self.labelsCorresp = {}
        self.nodesLabels = nodesLabels
        self.pairs = pairs
        self.nodes = {}
        for label in nodesLabels:
            if not label in self.nodes:
                self.nodes[label] = Node(label)
        for pair in pairs:
            node1 = self.nodes[pair[0]]
            node2 = self.nodes[pair[1]]
            node1.addOutputNode(node2)
            node2.addInputNode(node1)
        if labelsCorresp is not None:
            self.labelsCorresp = labelsCorresp
        else:
            [self.labelsCorresp, self.invLabelsCorresp] = self.detectSequences(enableSequenceDetection)
            self.newPairs = self.mapPairs()
        if invLabelsCorresp is not None:
            self.invLabelsCorresp = invLabelsCorresp
        if origPairs is not None:
            self.origPairs = origPairs
        if origLabels is not None:
            self.origLabels = origLabels

    def formGroupedGraph(self):
        """
        forms the clustered graph
        """
        return DfgGraph(list(self.labelsCorresp.keys()), self.newPairs, labelsCorresp=self.labelsCorresp,
                        invLabelsCorresp=self.invLabelsCorresp, origPairs=self.pairs, origLabels=self.nodesLabels)

    def mapPairs(self):
        """
        map original pairs between labels into clustered pairs
        """
        newPairs = []
        for pair in self.pairs:
            newPair = [self.invLabelsCorresp[pair[0]], self.invLabelsCorresp[pair[1]]]
            if not newPair[0] == newPair[1]:
                if not newPair in newPairs:
                    newPairs.append(newPair)
        return newPairs

    def getPairs(self):
        """
        gets pairs currently present in the graph
        """
        pairs = []
        for node in self.nodes.values():
            for otherNode in node.outputNodes:
                newPair = [str(node), str(otherNode)]
                if not newPair in pairs:
                    pairs.append(newPair)
        return pairs

    def getOrigPairs(self):
        """
        get original pairs (when graph gets clustered)
        """
        return self.origPairs

    def getOrigLabels(self):
        """
        get original labels (when graph gets clustered)
        """
        return self.origLabels

    def detectSequences(self, enableSequenceDetection):
        """
        detect clusters of sequential activities
        """
        simpleCouples = self.detectSimpleCouples(enableSequenceDetection)
        groupedActivities = deepcopy(simpleCouples)
        while True:
            oldGroupedActivities = deepcopy(groupedActivities)
            i = 0
            mustBreak = False
            while i < len(groupedActivities):
                j = 0
                while j < len(groupedActivities):
                    if not i == j:
                        if groupedActivities[i][-1] == groupedActivities[j][0]:
                            groupedActivities[i] = groupedActivities[i] + groupedActivities[j]
                            del groupedActivities[j]
                            mustBreak = True
                            break
                    j = j + 1
                if mustBreak:
                    break
                i = i + 1
            if groupedActivities == oldGroupedActivities:
                break
        groupedActivitiesFlattened = [item for sublist in groupedActivities for item in sublist]
        for label in self.nodesLabels:
            if not label in groupedActivitiesFlattened:
                groupedActivities.append([label])
        groupIndex = 0
        labelsCorresp = {}
        invLabelsCorresp = {}
        for ga in groupedActivities:
            groupIndex = groupIndex + 1
            labelsCorresp["group" + str(groupIndex)] = ga
            for ac in ga:
                invLabelsCorresp[ac] = "group" + str(groupIndex)
        return [labelsCorresp, invLabelsCorresp]

    def detectSimpleCouples(self, enableSequenceDetection):
        """
        support function in detecting clusters of sequential activities
        """
        simpleCouples = []
        if enableSequenceDetection:
            for node in self.nodes.values():
                if len(node.outputNodes) == 1:
                    otherNode = node.outputNodes[0]
                    if len(otherNode.inputNodes) == 1:
                        simpleCouples.append([str(node), str(otherNode)])
        return simpleCouples

    def getNodesWithNoInput(self):
        """
        gets nodes having no edges as input
        """
        nodesWithNoInput = []
        for nodeLabel in self.nodes:
            node = self.nodes[nodeLabel]
            if len(node.inputNodes) == 0:
                nodesWithNoInput.append(node)
        return nodesWithNoInput

    def getNodesWithNoOutput(self):
        """
        gets nodes having no edges as output
        """
        nodesWithNoOutput = []
        for nodeLabel in self.nodes:
            node = self.nodes[nodeLabel]
            if len(node.outputNodes) == 0:
                nodesWithNoOutput.append(node)
        return nodesWithNoOutput

    def activitiesAreAllConcurrent(self):
        """
        check if activities in the graph are all concurrent
        """
        for nodeLabel in self.nodes:
            node = self.nodes[nodeLabel]
            if len(node.outputNodes) > 0 or len(node.inputNodes) > 0:
                return False
        return True

    def negate(self):
        """
        negate the graph
        (to detect parallelism between activities)
        """
        for nodeLabel in self.nodes:
            node = self.nodes[nodeLabel]
            inputNodes = copy(node.inputNodes)
            outputNodes = copy(node.outputNodes)
            # print(node,inputNodes,outputNodes)
            for otherNode in inputNodes:
                if otherNode in outputNodes:
                    del node.inputNodes[node.inputNodes.index(otherNode)]
                    del node.outputNodes[node.outputNodes.index(otherNode)]
            outputNodeLabels = [str(x) for x in node.outputNodes]
            outputNodeLabels = set(outputNodeLabels)
            pairs = copy(self.pairs)
            for pair in pairs:
                if pair[0] == nodeLabel:
                    if pair[1] not in outputNodeLabels:
                        del self.pairs[self.pairs.index(pair)]
            pairsLabels = [str(x) for x in self.pairs]
            origPairs = copy(self.origPairs)
            for pair in origPairs:
                act0 = self.invLabelsCorresp[pair[0]]
                act1 = self.invLabelsCorresp[pair[1]]
                label = "['" + act0 + "', '" + act1 + "']"
                if not label in pairsLabels:
                    del self.origPairs[self.origPairs.index(pair)]

    # print(pairsLabels)

    def projectPairs(self, labels, pairs):
        """
        keep only pairs that have both elements inside labels list

        Parameters
        ----------
        labels
            Labels for which we want to do the projection
        pairs
            Pairs to project
        """
        newPairs = [x for x in pairs if x[0] in labels and x[1] in labels]
        return newPairs

    def formConnectedComponent(self, connectedLabels, elToExam, alreadyExamined, currentConnComp, recDepth):
        """
        recursive function to get a single connected component

        Parameters
        ----------
        connectedLabels
            For each label, maps the elements that are connected in input or in output
        elToExam
            Label to examine (we want to find the connected component containing it)
        alreadyExamined
            Already examined labels in this step
        currentConnComp
            Connected component (starts empty, and labels are added to it)
        recDepth
            Current recursion depth
        """

        if not elToExam in currentConnComp:
            currentConnComp.append(elToExam)
        if not elToExam in alreadyExamined:
            alreadyExamined.append(elToExam)
        for otherEl in connectedLabels[elToExam]:
            if not otherEl in currentConnComp:
                currentConnComp.append(otherEl)
            if not otherEl in alreadyExamined:
                [alreadyExamined, currentConnComp] = self.formConnectedComponent(connectedLabels, otherEl,
                                                                                 alreadyExamined, currentConnComp,
                                                                                 recDepth + 1)
        return [alreadyExamined, currentConnComp]

    def findConnectedComponents(self):
        """
        Find all connected components in the graph
        """

        # For each label, maps the elements that are connected in input or in output
        connectedLabels = {}
        for l in self.origLabels:
            connectedLabels[l] = set()
        for p in self.origPairs:
            connectedLabels[p[0]].add(p[1])
            connectedLabels[p[1]].add(p[0])

        # find the single connected components by iterating on the labels
        connectedComponents = []
        allAlreadyExamined = set()
        for el in connectedLabels.keys():
            if not el in allAlreadyExamined:
                [alreadyExamined, currentConnComp] = self.formConnectedComponent(connectedLabels, el, [], [], 0)
                connectedComponents.append(currentConnComp)
                for x in alreadyExamined:
                    allAlreadyExamined.add(x)
        return connectedComponents

    def findMaximumCut(self, addedGraphs):
        """
        finds the maximum cut of the graph
        """
        return self.findMaximumCutGreedy(addedGraphs)

    def getSetStrings(self, set):
        """
        Maps a set of nodes into activities names
        """
        setString = [str(x) for x in set]
        return setString

    def getNodesThatCanBeMoved(self, set1, set2, set1Strings, set2Strings, setToConsider):
        """
        Gets nodes that can be moved from a set to the other (for greedy maximum cut algorithm)

        Parameters
        ----------
        set1
            First set of maximum cut
        set2
            Second set of maximum cut
        set1Strings
            Strings related to activities in the first set
        set2Strings
            Strings related to activities in the second set
        setToConsider
            specify set1 or set2 as the set where to search a move
        """
        nodesThatCanBeMoved = []
        if setToConsider == "set1":
            for node in set1:
                canBeMoved = True
                for outputNode in node.outputNodes:
                    if str(outputNode) in set1Strings:
                        canBeMoved = False
                if canBeMoved:
                    nodesThatCanBeMoved.append(node)
        if setToConsider == "set2":
            for node in set2:
                canBeMoved = True
                for outputNode in node.outputNodes:
                    if str(outputNode) in set2Strings:
                        canBeMoved = False
                if canBeMoved:
                    nodesThatCanBeMoved.append(node)
        return nodesThatCanBeMoved

    def findMaximumCutAlgo2(self, addedGraphs):
        """
        Slower algorithm for maximum cut detection
        (examines all possibilities)

        Parameters
        ----------
        addedGraphs
            Part of the tree already added to the model
        """

        pairs = self.pairs
        activities = [str(x) for x in sorted(list(self.nodes.values()), key=lambda x: x.countConnections, reverse=True)]
        nodesOutputActivities = {}
        nodesInputActivities = {}
        for nodeLabel in self.nodes:
            node = self.nodes[nodeLabel]
            nodesInputActivities[nodeLabel] = set()
            nodesOutputActivities[nodeLabel] = set()
            for otherNodeLabel in node.outputNodes:
                nodesOutputActivities[nodeLabel].add(str(otherNodeLabel))
            for otherNodeLabel in node.inputNodes:
                nodesInputActivities[nodeLabel].add(str(otherNodeLabel))
        currentChoice = {}
        currentChoice["set1"] = set()
        currentChoice["set2"] = set()

        cutResult = CutResultObj()
        cutResult.findMaximumCutAlgo2Rec(currentChoice, activities, pairs, nodesInputActivities, nodesOutputActivities,
                                         0)

        if len(cutResult.optimalChoice["set1"]) > 0 and len(cutResult.optimalChoice["set2"]) > 0:
            # print("\nset1",cutResult.optimalChoice["set1"],"set2",cutResult.optimalChoice["set2"])

            set1Strings = cutResult.optimalChoice["set1"]
            set2Strings = cutResult.optimalChoice["set2"]
            retSet1 = [y for x in set1Strings for y in self.labelsCorresp[x]]
            retSet2 = [y for x in set2Strings for y in self.labelsCorresp[x]]
            return [True, retSet1, retSet2]

        return [False, [], []]

    def findMaximumCutGreedy(self, addedGraphs):
        """
        Greedy strategy to form a maximum cut:
        - activities without any input are added to set1
        - activities without any output are added to set2
        - if an activity cannot be added nor to set1 or to set2, then a cut is not found
        - other activities are added to the most convenient set
        """
        set1 = self.getNodesWithNoInput()
        set2 = self.getNodesWithNoOutput()
        set2 = [x for x in set2 if not x in set1]
        set1Strings = self.getSetStrings(set1)
        set2Strings = self.getSetStrings(set2)
        # set1NodesThatCanBeMoved = self.getNodesThatCanBeMoved(set1, set2, set1Strings, set2Strings, "set1")
        # set2NodesThatCanBeMoved = self.getNodesThatCanBeMoved(set1, set2, set1Strings, set2Strings, "set2")
        """print("set1Strings=",set1Strings)
        print("set2Strings=",set2Strings)
        print("set1NodesThatCanBeMoved=",set1NodesThatCanBeMoved)
        print("set2NodesThatCanBeMoved=",set2NodesThatCanBeMoved)
        input()"""

        nodes = sorted(list(self.nodes.values()), key=lambda x: x.countConnections, reverse=True)
        for node in nodes:
            if not node in set1 and not node in set2:
                inputConnectionsInSet1 = [x for x in self.pairs if x[0] in set1Strings]
                inputConnectionsInSet2 = [x for x in self.pairs if x[0] in set2Strings]
                outputConnectionsInSet1 = [x for x in self.pairs if x[1] in set1Strings]
                outputConnectionsInSet2 = [x for x in self.pairs if x[1] in set2Strings]
                if outputConnectionsInSet1 and inputConnectionsInSet2:
                    # impossible situation, not cut found
                    return [False, [], []]
                if addedGraphs or len(set1) == 0:
                    if outputConnectionsInSet1:
                        # must belong to set 1
                        set1.append(node)
                    elif inputConnectionsInSet2:
                        # must belong to set 2
                        set2.append(node)
                    else:
                        # add it to the most convenient place
                        """if len(set1) == 0:
                            # add to set 1
                            set1.append(node)
                        elif len(set2) == 0:
                            # add to set 2
                            set2.append(node)"""
                        if len(inputConnectionsInSet1) >= len(outputConnectionsInSet2):
                            # add to set 2
                            set2.append(node)
                        else:
                            # add to set 1
                            set1.append(node)
                else:
                    set2.append(node)
            set1Strings = self.getSetStrings(set1)
            set2Strings = self.getSetStrings(set2)
        # set1NodesThatCanBeMoved = self.getNodesThatCanBeMoved(set1, set2, set1Strings, set2Strings, "set1")
        # set2NodesThatCanBeMoved = self.getNodesThatCanBeMoved(set1, set2, set1Strings, set2Strings, "set2")
        set2 = [x for x in set2 if not x in set1]
        retSet1 = [y for x in set1Strings for y in self.labelsCorresp[x]]
        retSet2 = [y for x in set2Strings for y in self.labelsCorresp[x]]
        if len(retSet1) > 0 and len(retSet2) > 0:
            return [True, retSet1, retSet2]

        set1NodesThatCanBeMoved = self.getNodesThatCanBeMoved(set1, set2, set1Strings, set2Strings, "set1")
        set2NodesThatCanBeMoved = self.getNodesThatCanBeMoved(set1, set2, set1Strings, set2Strings, "set2")

        if len(set2) == 0 and len(set1NodesThatCanBeMoved) > 0:
            # print("moving to 2")
            set2.append(set1NodesThatCanBeMoved[0])
            del set1[set1.index(set1NodesThatCanBeMoved[0])]
            set1Strings = self.getSetStrings(set1)
            set2Strings = self.getSetStrings(set2)
            retSet1 = [y for x in set1Strings for y in self.labelsCorresp[x]]
            retSet2 = [y for x in set2Strings for y in self.labelsCorresp[x]]
            return [True, retSet1, retSet2]
        if len(set1) == 0 and len(set2NodesThatCanBeMoved) > 0:
            # print("moving to 1")
            set1.append(set2NodesThatCanBeMoved[0])
            del set2[set2.index(set2NodesThatCanBeMoved[0])]
            set1Strings = self.getSetStrings(set1)
            set2Strings = self.getSetStrings(set2)
            retSet1 = [y for x in set1Strings for y in self.labelsCorresp[x]]
            retSet2 = [y for x in set2Strings for y in self.labelsCorresp[x]]
            return [True, retSet1, retSet2]
        return [False, retSet1, retSet2]

    """def getSelfLoopStartingFromActivityIfExisting(self, activity, activitiesInputs, activitiesOutputs, allActivities):
        startActivities = set()
        endActivities = set()
        startActivities.add(activity)
        for act0 in startActivities:
            if act0 in activitiesInputs:
                for act1 in activitiesInputs[act0]:
                    if not act0 == act1 and not act1 in endActivities and not act1 in startActivities:
                        endActivities.add(act1)
        for act0 in endActivities:
            if act0 in activitiesOutputs:
                for act1 in activitiesOutputs[act0]:
                    if not act0 == act1 and not act1 in startActivities and not act1 in endActivities:
                        startActivities.add(act1)
        for act0 in startActivities:
            if act0 in activitiesInputs:
                for act1 in activitiesInputs[act0]:
                    if not (act1 in startActivities or act1 in endActivities):
                        return [False, set(), set()]
        for activity in allActivities:
            if not activity in startActivities and not activity in endActivities:
                startActivities.add(activity)
        intersection = set.intersection(startActivities, endActivities)
        return [True, list(startActivities), list(endActivities)]

    def findLoopCut(self):
        activitiesInputs = {}
        activitiesOutputs = {}
        allActivities = [str(x) for x in self.origLabels]

        for p in self.origPairs:
            if not p[1] in activitiesInputs:
                activitiesInputs[p[1]] = []
            if not p[0] in activitiesOutputs:
                activitiesOutputs[p[0]] = []
            activitiesInputs[p[1]].append(p[0])
            activitiesOutputs[p[0]].append(p[1])
        bestResult = None
        bestResultScore = -1
        for activity in self.origLabels:
            # result = self.discoverIfActivityIsStartEndInALoop(activity, activity, activitiesInputs, activitiesOutputs, deepcopy(set()), 0)
            result = self.getSelfLoopStartingFromActivityIfExisting(activity, activitiesInputs, activitiesOutputs,
                                                                    allActivities)
            if result[0]:
                score = min(len(result[1]), len(result[2]))
                if score > bestResultScore:
                    bestResult = result
                    bestResultScore = score
        return bestResult"""

    def findLoopCut(self, activitiesArcsDirection):
        """
        Finds a loop cut (alternative algorithm)

        Parameters
        ----------
        activitiesArcsDirection
            Activities arcs direction
        """
        activitiesInputs = {}
        activitiesOutputs = {}
        allActivities = [str(x) for x in self.origLabels]
        for p in self.origPairs:
            if not p[1] in activitiesInputs:
                activitiesInputs[p[1]] = []
            if not p[0] in activitiesOutputs:
                activitiesOutputs[p[0]] = []
            activitiesInputs[p[1]].append(p[0])
            activitiesOutputs[p[0]].append(p[1])
        activitiesUnderNegativeThreshold = []
        activitiesOverPositiveThreshold = []
        for act in activitiesArcsDirection:
            if activitiesArcsDirection[act] > LOOP_CONSTANT:
                activitiesOverPositiveThreshold.append(act)
            if activitiesArcsDirection[act] < -LOOP_CONSTANT:
                activitiesUnderNegativeThreshold.append(act)
        #print("activitiesArcsDirection=",activitiesArcsDirection)
        #print("activitiesUnderNegativeThreshold=", activitiesUnderNegativeThreshold)
        #print("activitiesOverPositiveThreshold=", activitiesOverPositiveThreshold)
        if len(activitiesOverPositiveThreshold) > 0:
            startActivities = copy(activitiesOverPositiveThreshold)
            endActivities = []

            for act in activitiesArcsDirection:
                if activitiesArcsDirection[act] < 0:
                    if not act in startActivities and not act in endActivities:
                        endActivities.append(act)
            for act in startActivities:
                for otherAct in activitiesInputs[act]:
                    if not otherAct in startActivities and not otherAct in endActivities:
                        if activitiesArcsDirection[otherAct] < 0:
                            endActivities.append(otherAct)
            for act in allActivities:
                if not (act in startActivities or act in endActivities):
                    startActivities.append(act)
            if startActivities and endActivities:
                return [True, startActivities, endActivities]
        elif len(activitiesUnderNegativeThreshold) > 0:
            startActivities = []
            endActivities = copy(activitiesUnderNegativeThreshold)
            for act in allActivities:
                if not (act in startActivities or act in endActivities):
                    startActivities.append(act)
            if startActivities and endActivities:
                return [True, startActivities, endActivities]
        return [False, [], []]
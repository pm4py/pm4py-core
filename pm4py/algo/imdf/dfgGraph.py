from copy import deepcopy
import random

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
	def __init__(self, nodesLabels, pairs, labelsCorresp = None, invLabelsCorresp = None, origPairs = None, origLabels = None, enableSequenceDetection = False):
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
		return DfgGraph(list(self.labelsCorresp.keys()), self.newPairs, labelsCorresp = self.labelsCorresp, invLabelsCorresp = self.invLabelsCorresp, origPairs = self.pairs, origLabels=self.nodesLabels)
	
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
			labelsCorresp["group"+str(groupIndex)] = ga
			for ac in ga:
				invLabelsCorresp[ac] = "group"+str(groupIndex)
		return [labelsCorresp,invLabelsCorresp]
	
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
			inputNodes = deepcopy(node.inputNodes)
			outputNodes = deepcopy(node.outputNodes)
			for otherNode in inputNodes:
				if otherNode in outputNodes:
					del node.inputNodes[node.inputNodes.index(otherNode)]
					del node.outputNodes[node.outputNodes.index(otherNode)]
			outputNodeLabels = [str(x) for x in node.outputNodes]
			pairs = deepcopy(self.origPairs)
			for pair in pairs:
				if pair[0] == nodeLabel and pair[1] not in outputNodeLabels:
					del self.pairs[self.pairs.index(pair)]
	
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
	
	def formConnectedComponent(self,connectedLabels,elToExam,alreadyExamined,currentConnComp,recDepth):
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
				[alreadyExamined,currentConnComp] = self.formConnectedComponent(connectedLabels,otherEl,alreadyExamined,currentConnComp,recDepth+1)
		return [alreadyExamined,currentConnComp]
	
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
				[alreadyExamined,currentConnComp] = self.formConnectedComponent(connectedLabels,el,[],[],0)
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
		setString = [str(x) for x in set]
		return setString
	
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
		set2Strings = self.getSetStrings(set1)
		#print("set1Strings = "+str(set1Strings))
		#print("set2Strings = "+str(set2Strings))
		#print("origPairs = "+str(self.origPairs))
		#print("origLabels = "+str(self.origLabels))
		#print("labelsCorresp = "+str(self.labelsCorresp))
		#print("invLabelsCorresp = "+str(self.invLabelsCorresp))
		#print("pairs = "+str(self.pairs))
		nodes = sorted(list(self.nodes.values()), key=lambda x: x.countConnections, reverse=True)
		for node in nodes:
			if not node in set1 and not node in set2:
				inputConnectionsInSet1 = [x for x in self.pairs if x[0] in set1Strings]
				inputConnectionsInSet2 = [x for x in self.pairs if x[0] in set2Strings]
				outputConnectionsInSet1 = [x for x in self.pairs if x[1] in set1Strings]
				outputConnectionsInSet2 = [x for x in self.pairs if x[1] in set2Strings]	
				if outputConnectionsInSet1 and inputConnectionsInSet2:
					# impossible situation, not cut found
					return [False,[],[]]
				if addedGraphs:
					if outputConnectionsInSet1:
						# must belong to set 1
						set1.append(node)
					elif inputConnectionsInSet2:
						# must belong to set 2
						set2.append(node)
					else:
						# add it to the most convenient place
						if len(inputConnectionsInSet1) >= len(outputConnectionsInSet2):
							# add to set 1
							set1.append(node)
						else:
							# add to set 2
							set2.append(node)
				else:
					set2.append(node)
			set1Strings = self.getSetStrings(set1)
			set2Strings = self.getSetStrings(set2)
		retSet1 = [y for x in set1Strings for y in self.labelsCorresp[x]]
		retSet2 = [y for x in set2Strings for y in self.labelsCorresp[x]]
		if len(retSet1) > 0 and len(retSet2) > 0:
			return [True,retSet1,retSet2]
		return [False,retSet1,retSet2]
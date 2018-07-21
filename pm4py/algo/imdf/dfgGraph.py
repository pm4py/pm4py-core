from copy import deepcopy
import random

class Node(object):
	def __init__(self, label):
		self.label = label
		self.countConnections = 0
		self.inputNodes = []
		self.outputNodes = []
	
	def addInputNode(self, node):
		self.inputNodes.append(node)
		self.countConnections = self.countConnections + 1
	
	def addOutputNode(self, node):
		self.outputNodes.append(node)
		self.countConnections = self.countConnections + 1
	
	def __repr__(self):
		return self.label
	
class DfgGraph(object):
	def __init__(self, nodesLabels, pairs, labelsCorresp = None, invLabelsCorresp = None, origPairs = None):
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
			[self.labelsCorresp, self.invLabelsCorresp] = self.detectSequences()
			self.newPairs = self.mapPairs()
		if invLabelsCorresp is not None:
			self.invLabelsCorresp = invLabelsCorresp
		if origPairs is not None:
			self.origPairs = origPairs
	
	def formGroupedGraph(self):
		return DfgGraph(list(self.labelsCorresp.keys()), self.newPairs, labelsCorresp = self.labelsCorresp, invLabelsCorresp = self.invLabelsCorresp, origPairs = self.pairs)
	
	def mapPairs(self):
		newPairs = []
		for pair in self.pairs:
			newPair = [self.invLabelsCorresp[pair[0]], self.invLabelsCorresp[pair[1]]]
			if not newPair[0] == newPair[1]:
				if not newPair in newPairs:
					newPairs.append(newPair)
		return newPairs
	
	def getPairs(self):
		pairs = []
		for node in self.nodes.values():
			for otherNode in node.outputNodes:
				newPair = [str(node), str(otherNode)]
				if not newPair in pairs:
					pairs.append(newPair)
		return pairs
	
	def getOrigPairs(self):
		return self.origPairs
	
	def detectSequences(self):
		simpleCouples = self.detectSimpleCouples()
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
	
	def detectSimpleCouples(self):
		simpleCouples = []
		for node in self.nodes.values():
			if len(node.outputNodes) == 1:
				otherNode = node.outputNodes[0]
				if len(otherNode.inputNodes) == 1:
					simpleCouples.append([str(node), str(otherNode)])
		return simpleCouples
	
	def projectPairs(self, labels, pairs):
		newPairs = [x for x in pairs if x[0] in labels and x[1] in labels]
		return newPairs
	
	def getNodesWithNoInput(self):
		nodesWithNoInput = []
		for nodeLabel in self.nodes:
			node = self.nodes[nodeLabel]
			if len(node.inputNodes) == 0:
				nodesWithNoInput.append(node)
		return nodesWithNoInput
	
	def getNodesWithNoOutput(self):
		nodesWithNoOutput = []
		for nodeLabel in self.nodes:
			node = self.nodes[nodeLabel]
			if len(node.outputNodes) == 0:
				nodesWithNoOutput.append(node)
		return nodesWithNoOutput
	
	def activitiesAreAllConcurrent(self):
		for nodeLabel in self.nodes:
			node = self.nodes[nodeLabel]
			if len(node.outputNodes) > 0 or len(node.inputNodes) > 0:
				return False
		return True
	
	def negate(self):
		for nodeLabel in self.nodes:
			node = self.nodes[nodeLabel]
			inputNodes = deepcopy(node.inputNodes)
			outputNodes = deepcopy(node.outputNodes)
			for otherNode in inputNodes:
				if otherNode in outputNodes:
					del node.inputNodes[node.inputNodes.index(otherNode)]
					del node.outputNodes[node.outputNodes.index(otherNode)]

	def findMaximumCut(self):
		return self.findMaximumCutGreedy()
	
	def findMaximumCutGreedy(self):
		set1 = self.getNodesWithNoInput()
		set2 = self.getNodesWithNoOutput()
		nodes = sorted(list(self.nodes.values()), key=lambda x: x.countConnections, reverse=True)
		addTo = set1
		for node in nodes:
			if not node in set1 and not node in set2:
				# try add the node to set 1
				addOk = True
				for otherNode in set2:
					if otherNode in node.inputNodes:
						addOk = False
						break
				if not addOk:
					addOk = True
					addTo = set2
					# try add the node to set 2
					for otherNode in set1:
						if otherNode in node.outputNodes:
							addOk = False
							break
					if not addOk:
						# no cut found by greedy strategy: return False
						return [False,[],[]]
				addTo.append(node)
		
		set1 = [str(x) for x in set1]
		set2 = [str(x) for x in set2]
		set1 = [y for x in set1 for y in self.labelsCorresp[x]]
		set2 = [y for x in set2 for y in self.labelsCorresp[x]]
		
		if len(set1)>0 and len(set2)>0:
			return [True,set1,set2]
		return [False,set1,set2]
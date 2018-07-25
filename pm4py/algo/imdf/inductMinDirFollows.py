from pm4py.log.util import trace_log as tl_util
from pm4py.algo.dfg import instance as dfg_inst
from pm4py.algo.imdf.dfgGraph import DfgGraph as DfgGraph
from pm4py.models import petri
from pm4py.models.petri.net import Marking

import time
from copy import deepcopy

class InductMinDirFollows(object):
	def __init__(self):
		"""
		Constructor
		"""
		self.addedGraphs = []
		self.noOfPlacesAdded = 0
		self.noOfTransitionsAdded = 0
		self.noOfHiddenTransAdded = 0
		self.lastEndSubtreePlaceAdded = []
		self.transitionsMap = {}
		self.addedArcsObjLabels = []
	
	def cleanDfg(self, dfg):
		dfgMap = {}
		for el in dfg:
			dfgMap[str(el[0])] = el[1]
		"""i = 0
		while i < len(dfg):
			el = dfg[i][0]
			elStr = str(el)
			elStrOcc = dfgMap[elStr]
			elInvStr = str((el[1], el[0]))
			if elInvStr in dfgMap:
				elInvStrOcc = dfgMap[elInvStr]
			i = i + 1"""
		return dfg
	
	def apply(self, trace_log, activity_key='concept:name'):
		"""
		Apply the Inductive Miner directly follows algorithm.
		
		Parameters
		----------
		trace_log : :class:`pm4py.log.instance.TraceLog`
			Event log to use in the alpha miner, note that it should be a TraceLog!
		activity_key : `str`, optional
			Key to use within events to identify the underlying activity.
			By deafult, the value 'concept:name' is used.
		
		Returns
		-------
		net : :class:`pm4py.models.petri.instance.PetriNet`
			A Petri net describing the event log that is provided as an input
		
		References
		----------
		Leemans, S. J., Fahland, D., & van der Aalst, W. M. (2015, June). Scalable process discovery with guarantees. In International Conference on Enterprise, Business-Process and Information Systems Modeling (pp. 85-101). Springer, Cham.
		"""
		labels = tl_util.fetch_labels(trace_log, activity_key)
		#alpha_abstraction = ds.ClassicAlphaAbstraction(trace_log, activity_key)
		#pairs = list(alpha_abstraction.causal_relation)
		dfg = [(k,v) for k, v in dfg_inst.compute_dfg(trace_log, activity_key).items() if v > 0]
		dfg = sorted(dfg, key=lambda x: x[1], reverse=True)
		dfg = self.cleanDfg(dfg)
		pairs = [k[0] for k in dfg]
		labels = [str(x) for x in labels]
		pairs = [(str(x[0]),str(x[1])) for x in pairs]
		net = petri.net.PetriNet('imdf_net_' + str(time.time()))
		start = petri.net.PetriNet.Place('start')
		net.places.add(start)
		self.lastEndSubtreePlaceAdded = [start]
		net = self.recFindCut(net, labels, pairs, 0, self.lastEndSubtreePlaceAdded)
		return net, Marking({start: 1})
	
	def addSubtreeToModel(self, net, labels, type, dfgGraph, refToLastPlace, addSkipTransition=True):
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
		self.noOfPlacesAdded = self.noOfPlacesAdded + 1
		subtreeEnd = petri.net.PetriNet.Place('p_'+str(self.noOfPlacesAdded))
		net.places.add(subtreeEnd)
		if self.addedGraphs:
			if addSkipTransition:
				# add the hidden transitions that permits to skip the tree
				self.noOfHiddenTransAdded = self.noOfHiddenTransAdded + 1
				hiddenTransSkipTree = petri.net.PetriNet.Transition('tau_'+str(self.noOfHiddenTransAdded), 'tau_'+str(self.noOfHiddenTransAdded))
				net.transitions.add(hiddenTransSkipTree)
				#net.arcs.add(petri.net.PetriNet.Arc(refToLastPlace[0], hiddenTransSkipTree))
				#net.arcs.add(petri.net.PetriNet.Arc(hiddenTransSkipTree, subtreeEnd))
				petri.utils.add_arc_from_to(refToLastPlace[0], hiddenTransSkipTree, net)
				petri.utils.add_arc_from_to(hiddenTransSkipTree, subtreeEnd, net)

			if type == "flower":
				# if we are adding a flower, we must add also the coming back arc
				self.noOfHiddenTransAdded = self.noOfHiddenTransAdded + 1
				hiddenTransLoop = petri.net.PetriNet.Transition('tau_'+str(self.noOfHiddenTransAdded), 'tau_'+str(self.noOfHiddenTransAdded))
				net.transitions.add(hiddenTransLoop)
				#net.arcs.add(petri.net.PetriNet.Arc(hiddenTransLoop, refToLastPlace[0]))
				#net.arcs.add(petri.net.PetriNet.Arc(subtreeEnd, hiddenTransLoop))
				petri.utils.add_arc_from_to(hiddenTransLoop, refToLastPlace[0], net)
				petri.utils.add_arc_from_to(subtreeEnd, hiddenTransLoop, net)

		# each label is a cluster of sequentially followed activities
		for l in labels:			
			transitions = []
			hiddenTransitionsInput = []
			hiddenTransitionsOutput = []
			hiddenTransitionsInputPlaces = []
			hiddenTransitionsOutputPlaces = []
			i = 0
			while i < len(l):
				li = l[i]
				self.noOfTransitionsAdded = self.noOfTransitionsAdded + 1
				transLab = li
				# add the transitions to the model if needed
				if not transLab in self.transitionsMap:
					transObj = petri.net.PetriNet.Transition('t_'+str(self.noOfTransitionsAdded), li)
					transitions.append(transObj)
					self.transitionsMap[transLab] = transObj
					net.transitions.add(transitions[-1])
				else:
					transitions.append(self.transitionsMap[transLab])
				# input element of the sequence cluster
				if i == 0:
					if type == "parallel":
						# if we must add a parallel subtree, then hidden transitions are added to the model
						self.noOfHiddenTransAdded = self.noOfHiddenTransAdded + 1
						hiddenTransitionsInput.append(petri.net.PetriNet.Transition('tau_'+str(self.noOfHiddenTransAdded), 'tau_'+str(self.noOfHiddenTransAdded)))
						net.transitions.add(hiddenTransitionsInput[-1])
						self.noOfPlacesAdded = self.noOfPlacesAdded + 1
						hiddenTransitionsInputPlaces.append(petri.net.PetriNet.Place('p_'+str(self.noOfPlacesAdded)))
						net.places.add(hiddenTransitionsInputPlaces[-1])
						#net.arcs.add(petri.net.PetriNet.Arc(refToLastPlace[0], hiddenTransitionsInput[-1]))
						#net.arcs.add(petri.net.PetriNet.Arc(hiddenTransitionsInput[-1], hiddenTransitionsInputPlaces[-1]))
						petri.utils.add_arc_from_to(refToLastPlace[0], hiddenTransitionsInput[-1], net)
						petri.utils.add_arc_from_to(hiddenTransitionsInput[-1], hiddenTransitionsInputPlaces[-1], net)
					if type == "parallel":
						arcLabel = str(hiddenTransitionsInputPlaces[0]) + str(transitions[0])
						if not arcLabel in self.addedArcsObjLabels:
							#net.arcs.add(petri.net.PetriNet.Arc(hiddenTransitionsInputPlaces[0], transitions[0]))
							petri.utils.add_arc_from_to(hiddenTransitionsInputPlaces[0], transitions[0], net)
							self.addedArcsObjLabels.append(arcLabel)
					else:
						if type == "concurrent" or type == "flower":
							# if we are adding a concurrent or flower subtree, then we have no worries:
							# we need to add an arc between the previous place and the transition
							arcLabel = str(refToLastPlace[0]) + str(transitions[0])
							if not arcLabel in self.addedArcsObjLabels:
								#net.arcs.add(petri.net.PetriNet.Arc(refToLastPlace[0], transitions[0]))
								petri.utils.add_arc_from_to(refToLastPlace[0], transitions[0], net)
								self.addedArcsObjLabels.append(arcLabel)
						"""if type == "flower":
							# if we are adding a flower, we must add also the coming back arc
							arcLabel = str(transitions[0]) + str(refToLastPlace[0])
							if not arcLabel in self.addedArcsObjLabels:
								net.arcs.add(petri.net.PetriNet.Arc(transitions[0], refToLastPlace[0]))
								self.addedArcsObjLabels.append(arcLabel)"""
				if i > 0:
					# we add sequential elements inside the cluster
					if not transitions[-2].label == transitions[-1].label:
						arcLabel = str(transitions[-2]) + str(transitions[-1])
						if not arcLabel in self.addedArcsObjLabels:
							self.noOfPlacesAdded = self.noOfPlacesAdded + 1
							auxiliaryPlace = petri.net.PetriNet.Place('p_'+str(self.noOfPlacesAdded))
							net.places.add(auxiliaryPlace)
							#net.arcs.add(petri.net.PetriNet.Arc(transitions[-2], auxiliaryPlace))
							#net.arcs.add(petri.net.PetriNet.Arc(auxiliaryPlace, transitions[-1]))
							petri.utils.add_arc_from_to(transitions[-2], auxiliaryPlace, net)
							petri.utils.add_arc_from_to(auxiliaryPlace, transitions[-1], net)
							self.addedArcsObjLabels.append(arcLabel)
				if i == len(l)-1:
					if type == "parallel":
						# if we must add a parallel subtree, then hidden transitions are added to the model
						self.noOfHiddenTransAdded = self.noOfHiddenTransAdded + 1
						hiddenTransitionsOutput.append(petri.net.PetriNet.Transition('tau_'+str(self.noOfHiddenTransAdded), 'tau_'+str(self.noOfHiddenTransAdded)))
						net.transitions.add(hiddenTransitionsOutput[-1])
						self.noOfPlacesAdded = self.noOfPlacesAdded + 1
						hiddenTransitionsOutputPlaces.append(petri.net.PetriNet.Place('p_'+str(self.noOfPlacesAdded)))
						net.places.add(hiddenTransitionsOutputPlaces[-1])
						#net.arcs.add(petri.net.PetriNet.Arc(hiddenTransitionsOutputPlaces[-1], hiddenTransitionsOutput[-1]))
						#net.arcs.add(petri.net.PetriNet.Arc(hiddenTransitionsOutput[-1], subtreeEnd))
						petri.utils.add_arc_from_to(hiddenTransitionsOutputPlaces[-1], hiddenTransitionsOutput[-1], net)
						petri.utils.add_arc_from_to(hiddenTransitionsOutput[-1], subtreeEnd, net)
					if type == "parallel":
						arcLabel = str(transitions[-1]) + str(hiddenTransitionsOutputPlaces[-1])
						if not arcLabel in self.addedArcsObjLabels:
							#net.arcs.add(petri.net.PetriNet.Arc(transitions[-1], hiddenTransitionsOutputPlaces[-1]))
							petri.utils.add_arc_from_to(transitions[-1], hiddenTransitionsOutputPlaces[-1], net)
							self.addedArcsObjLabels.append(arcLabel)
					else:
						if type == "concurrent" or type == "flower":
							# if we are adding a concurrent or flower subtree, then we have no worries:
							# we need to add an arc between the transition and the end-subtree place
							arcLabel = str(transitions[-1]) + str(subtreeEnd)
							if not arcLabel in self.addedArcsObjLabels:
								#net.arcs.add(petri.net.PetriNet.Arc(transitions[-1], subtreeEnd))
								petri.utils.add_arc_from_to(transitions[-1], subtreeEnd, net)
								self.addedArcsObjLabels.append(arcLabel)
				i = i + 1
		refToLastPlace[0] = subtreeEnd
		self.addedGraphs.append(labels)
		return net
	
	def addConnectionPlace(self, net, newRefToLastPlace, inputConnectionPlace = None):
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
			connectionPlace = petri.net.PetriNet.Place('p_'+str(self.noOfPlacesAdded))
			net.places.add(connectionPlace)
		else:
			connectionPlace = inputConnectionPlace
		self.noOfHiddenTransAdded = self.noOfHiddenTransAdded + 1
		hiddenTransition = petri.net.PetriNet.Transition('tau_'+str(self.noOfHiddenTransAdded), 'tau_'+str(self.noOfHiddenTransAdded))
		net.transitions.add(hiddenTransition)
		#net.arcs.add(petri.net.PetriNet.Arc(newRefToLastPlace[0], hiddenTransition))
		#net.arcs.add(petri.net.PetriNet.Arc(hiddenTransition, connectionPlace))
		petri.utils.add_arc_from_to(newRefToLastPlace[0], hiddenTransition, net)
		petri.utils.add_arc_from_to(hiddenTransition, connectionPlace, net)

		return [net, connectionPlace, hiddenTransition]
		
	def recFindCut(self, net, nodesLabels, pairs, recDepth, refToLastPlace):
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
		if len(pairs) == 0:
			# we have all unconnected activities / clusters of sequential activities: add them to the model!
			net = self.addSubtreeToModel(net, list(dfgGraph.labelsCorresp.values()), "concurrent", dfgGraph, refToLastPlace)
		else:
			connectedComponents = dfgGraph.findConnectedComponents()
			# if we have more than one connected component, we do recursion to add them to the model
			if len(connectedComponents)>1:
				connectionPlace = None
				newRefToLastPlace = [deepcopy(refToLastPlace)[0]]
				for cc in connectedComponents:
					# we add the connected component and memorize the connection place
					ccPairs = dfgGraph.projectPairs(cc,origPairs)
					net = self.recFindCut(net, cc, ccPairs, recDepth + 1, newRefToLastPlace)
					[net, connectionPlace, connectionTransition] = self.addConnectionPlace(net, newRefToLastPlace, inputConnectionPlace=connectionPlace)
				refToLastPlace[0] = connectionPlace
			else:
				# we have only one connected component: find the maximum cut in the graph
				maximumCut = dfgGraph.findMaximumCut(self.addedGraphs)
				# if we have a plausible maximum cut, then recur and add the partition to the Petri net
				if maximumCut[0] and maximumCut[1] and maximumCut[2]:
					pairs1 = dfgGraph.projectPairs(maximumCut[1],origPairs)
					pairs2 = dfgGraph.projectPairs(maximumCut[2],origPairs)
					net = self.recFindCut(net, maximumCut[1], pairs1, recDepth + 1, refToLastPlace)					
					net = self.recFindCut(net, maximumCut[2], pairs2, recDepth + 1, refToLastPlace)
				else:
					# otherwise, negate the graph to observe parallel behavior
					dfgGraph.negate()
					negatedPairs = dfgGraph.getPairs()
					if len(negatedPairs) == 0:
						# in this case, we have a parallel subtree
						net = self.addSubtreeToModel(net, list(dfgGraph.labelsCorresp.values()), "parallel", dfgGraph, refToLastPlace)
					else:
						# otherwise, we have a flower subtree
						net = self.addSubtreeToModel(net, list(dfgGraph.labelsCorresp.values()), "flower", dfgGraph, refToLastPlace)
		return net
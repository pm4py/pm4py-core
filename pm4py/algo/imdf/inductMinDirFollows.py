from pm4py.log.util import trace_log as tl_util
from pm4py.algo.alpha import data_structures as ds
from pm4py.algo.imdf.dfgGraph import DfgGraph as DfgGraph
from pm4py.models.petri import instance as pn_instance

import time

class InductMinDirFollows(object):
	def __init__(self):
		self.addedGraphs = []
		self.noOfPlacesAdded = 0
		self.noOfTransitionsAdded = 0
		self.noOfHiddenTransAdded = 0
		self.lastEndSubtreePlaceAdded = None
	
	def apply(self, trace_log, activity_key='concept:name'):
		labels = tl_util.fetch_labels(trace_log, activity_key)
		alpha_abstraction = ds.ClassicAlphaAbstraction(trace_log, activity_key)
		pairs = list(alpha_abstraction.causal_relation)
		labels = [str(x) for x in labels]
		pairs = [(str(x[0]),str(x[1])) for x in pairs]
		net = pn_instance.PetriNet('alpha_classic_net_' + str(time.time()))
		start = pn_instance.PetriNet.Place('start')
		net.places.add(start)
		self.lastEndSubtreePlaceAdded = start
		net = self.recFindCut(net, labels, pairs, 0)
		
		return net
	
	def addSubtreeToModel(self, net, labels, type, dfgGraph):
		self.noOfPlacesAdded = self.noOfPlacesAdded + 1
		subtreeEnd = pn_instance.PetriNet.Place('p_'+str(self.noOfPlacesAdded))
		net.places.add(subtreeEnd)
		
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
				transitions.append(pn_instance.PetriNet.Transition('t_'+str(self.noOfTransitionsAdded), li))
				net.transitions.add(transitions[-1])
				
				if i == 0:
					if type == "parallel":
						self.noOfHiddenTransAdded = self.noOfHiddenTransAdded + 1
						hiddenTransitionsInput.append(pn_instance.PetriNet.Transition('tau_'+str(self.noOfHiddenTransAdded), 'tau_'+str(self.noOfHiddenTransAdded)))
						net.transitions.add(hiddenTransitionsInput[-1])
						self.noOfPlacesAdded = self.noOfPlacesAdded + 1
						hiddenTransitionsInputPlaces.append(pn_instance.PetriNet.Place('p_'+str(self.noOfPlacesAdded)))
						net.places.add(hiddenTransitionsInputPlaces[-1])
						net.arcs.add(pn_instance.PetriNet.Arc(self.lastEndSubtreePlaceAdded, hiddenTransitionsInput[-1]))
						net.arcs.add(pn_instance.PetriNet.Arc(hiddenTransitionsInput[-1], hiddenTransitionsInputPlaces[-1]))

					if type == "parallel":
						net.arcs.add(pn_instance.PetriNet.Arc(hiddenTransitionsInputPlaces[0], transitions[0]))
					else:
						if type == "concurrent" or type == "flower":
							net.arcs.add(pn_instance.PetriNet.Arc(self.lastEndSubtreePlaceAdded, transitions[0]))
						
						if type == "flower":
							net.arcs.add(pn_instance.PetriNet.Arc(transitions[0], self.lastEndSubtreePlaceAdded))
				
				if i > 0:
					self.noOfPlacesAdded = self.noOfPlacesAdded + 1
					auxiliaryPlace = pn_instance.PetriNet.Place('p_'+str(self.noOfPlacesAdded))
					net.places.add(auxiliaryPlace)
					net.arcs.add(pn_instance.PetriNet.Arc(transitions[-2], auxiliaryPlace))
					net.arcs.add(pn_instance.PetriNet.Arc(auxiliaryPlace, transitions[-1]))
				
				if i == len(l)-1:
					if type == "parallel":
						self.noOfHiddenTransAdded = self.noOfHiddenTransAdded + 1
						hiddenTransitionsOutput.append(pn_instance.PetriNet.Transition('tau_'+str(self.noOfHiddenTransAdded), 'tau_'+str(self.noOfHiddenTransAdded)))
						net.transitions.add(hiddenTransitionsOutput[-1])
						self.noOfPlacesAdded = self.noOfPlacesAdded + 1
						hiddenTransitionsOutputPlaces.append(pn_instance.PetriNet.Place('p_'+str(self.noOfPlacesAdded)))
						net.places.add(hiddenTransitionsOutputPlaces[-1])
						net.arcs.add(pn_instance.PetriNet.Arc(hiddenTransitionsOutputPlaces[-1], hiddenTransitionsOutput[-1]))
						net.arcs.add(pn_instance.PetriNet.Arc(hiddenTransitionsOutput[-1], subtreeEnd))
					if type == "parallel":
						net.arcs.add(pn_instance.PetriNet.Arc(transitions[-1], hiddenTransitionsOutputPlaces[-1]))
					else:
						if type == "concurrent" or type == "flower":
							net.arcs.add(pn_instance.PetriNet.Arc(transitions[-1], subtreeEnd))

				i = i + 1
		
		
		self.lastEndSubtreePlaceAdded = subtreeEnd
		self.addedGraphs.append(labels)
		
		return net
	
	def recFindCut(self, net, nodesLabels, pairs, recDepth):
		dfgGraph = DfgGraph(nodesLabels, pairs).formGroupedGraph()
		pairs = dfgGraph.getPairs()
		origPairs = dfgGraph.getOrigPairs()
		
		if len(pairs) == 0:
			print(recDepth,"activitiesAreAllConcurrent",nodesLabels)
			net = self.addSubtreeToModel(net, list(dfgGraph.labelsCorresp.values()), "concurrent", dfgGraph)
		else:
			maximumCut = dfgGraph.findMaximumCut()
			if maximumCut[0] and maximumCut[1] and maximumCut[2]:
				print(recDepth,"found maximum cut",maximumCut)
				pairs1 = dfgGraph.projectPairs(maximumCut[1],origPairs)
				pairs2 = dfgGraph.projectPairs(maximumCut[2],origPairs)
				print(recDepth,"maximumCut[1]=",maximumCut[1],"pairs1=",pairs1)
				net = self.recFindCut(net, maximumCut[1], pairs1, recDepth + 1)
				print(recDepth,"maximumCut[2]=",maximumCut[2],"pairs2=",pairs2)
				
				net = self.recFindCut(net, maximumCut[2], pairs2, recDepth + 1)
			else:
				dfgGraph.negate()
				negatedPairs = dfgGraph.getPairs()
				if len(negatedPairs) == 0:
					print(recDepth,"NEGATED activitiesAreAllConcurrent",nodesLabels)
					net = self.addSubtreeToModel(net, list(dfgGraph.labelsCorresp.values()), "parallel", dfgGraph)
				else:
					print(recDepth,"flower model")
					net = self.addSubtreeToModel(net, list(dfgGraph.labelsCorresp.values()), "flower", dfgGraph)
		
		return net
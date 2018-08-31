#from pm4py.algo.inductive.versions import dfg_only
from pm4py.algo.inductive import factory as inductive_factory
from pm4py.log.importer import xes as xes_importer
from pm4py.models.petri import visualize as pn_viz
from pm4py.algo.tokenreplay.versions import token_replay
from pm4py.algo.tokenreplay import factory as token_factory
import time

log = xes_importer.import_from_file_xes('tests\\inputData\\receipt.xes')
print("loaded log")
net, marking, final_marking = inductive_factory.apply(log)
for place in marking:
	print("initial marking "+place.name)
"""final_marking = petri.petrinet.Marking()
for p in net.places:
    if not p.out_arcs:
        final_marking[p] = 1"""
for place in final_marking:
	print("final marking "+place.name)
gviz = pn_viz.graphviz_visualization(net, initial_marking=marking, final_marking=final_marking, debug=False)
gviz.view()
time0 = time.time()
print("started token replay")
[traceIsFit, traceFitnessValue, activatedTransitions, placeFitness, reachedMarkings, enabledTransitionsInMarkings] = \
	token_factory.apply(log, net, marking, final_marking)
for place in placeFitness:
	if len(placeFitness[place]['underfedTraces']) > 0:
		print(place.name)
print("underfed places: ",[place.name for place in placeFitness.keys() if len(placeFitness[place]['underfedTraces']) > 0])
print("overfed places: ",[place.name for place in placeFitness.keys() if len(placeFitness[place]['overfedTraces']) > 0])
time1 = time.time()
print("time interlapsed",(time1-time0))
fitTraces = [x for x in traceIsFit if x]
fitness = float(len(fitTraces))/float(len(log))
print("fitness = "+str(fitness))
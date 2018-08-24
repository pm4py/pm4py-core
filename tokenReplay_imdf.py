#from pm4py.algo.inductive.versions import dfg_only
from pm4py.algo.inductive import factory as inductive_factory
from pm4py.log.importer import xes as xes_importer
from pm4py.models.petri import visualize as pn_viz
from pm4py.models import petri
from pm4py.algo.tokenreplay import token_replay
import time

log = xes_importer.import_from_file_xes('C:\\receipt.xes')
#log = xes_importer.import_from_path_xes('a32f0n00.xes')
net, marking = inductive_factory.apply(log)
for place in marking:
	print("initial marking "+place.name)
final_marking = petri.petrinet.Marking()
for p in net.places:
    if not p.out_arcs:
        final_marking[p] = 1
for place in final_marking:
	print("final marking "+place.name)
gviz = pn_viz.graphviz_visualization(net)
gviz.view()
log = log[0:min(100,len(log))]
time0 = time.time()
print("started token replay")
[traceIsFit, traceFitnessValue, activatedTransitions, placeFitness, reachedMarkings, enabledTransitionsInMarkings] = token_replay.apply_log(log, net, marking, final_marking, enable_placeFitness=True)
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

"""for trace in activatedTransitions:
	print("\n\n")
	for tr in trace:
		if tr.label is not None:
			print(tr.label)
		else:
			print(tr.name)"""
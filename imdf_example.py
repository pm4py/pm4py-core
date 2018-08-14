from pm4py.algo.imdf import inductMinDirFollows
from pm4py.log.importer import xes as xes_importer
from pm4py.models.petri import visualize as pn_viz
import pm4py.algo.alignments as align
from pm4py.algo.tokenreplay import token_replay
from pm4py.models import petri
import traceback

#log = xes_importer.import_from_path_xes('a32f0n00.xes')
log = xes_importer.import_from_path_xes('C:\\a32f0n00.xes')
net, marking = inductMinDirFollows.apply(log)
for place in marking:
	print("initial marking "+place.name)
final_marking = petri.net.Marking()
for p in net.places:
    if not p.out_arcs:
        final_marking[p] = 1
for place in final_marking:
	print("final marking "+place.name)
gviz = pn_viz.graphviz_visualization(net)
gviz.view()
print([x["concept:name"] for x in log[0]])
fitTraces = []
[traceIsFit, traceFitnessValue, activatedTransitions, placeFitness] = token_replay.apply_log(log, net, marking,
																							 final_marking,
																							 enable_placeFitness=True)
i = 0
while i < len(log):
	try:
		print("\n",i,[x["concept:name"] for x in log[i]])
		cfResult = align.versions.state_equation_classic.apply_trace(log[i], net, marking, final_marking)['alignment']
		if cfResult is None:
			print("alignment is none!")
		else:
			isFit = True
			for couple in cfResult:
				print(couple)
				if not (couple[0] == couple[1] or couple[0] == ">>" and couple[1] == None):
					isFit = False
			print("isFit = "+str(isFit))

			if isFit:
				fitTraces.append(log[i])

			"""if isFit and traceIsFit[i]:
				if len(cfResult) > len(activatedTransitions[i]):
					print("\n", i, [x["concept:name"] for x in log[i]])
					print(len(cfResult), len(activatedTransitions[i]))
					print(cfResult)
					print(activatedTransitions[i])"""
	except:
		print("EXCEPTION ",i)
		traceback.print_exc()
	i = i + 1
print(fitTraces)
print(len(fitTraces))
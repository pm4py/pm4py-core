#from pm4py.algo.inductive.versions import dfg_only
from pm4py.algo.inductive import factory as inductive_factory
from pm4py.log.importer import xes as xes_importer
from pm4py.models.petri import visualize as pn_viz
import pm4py.algo.alignments as align
from pm4py.algo.tokenreplay import token_replay
from pm4py.models import petri
import traceback
from pm4py.models.petri.exporter import pnml as petri_exporter

if __name__ == "__main__":
	#log = xes_importer.import_from_path_xes('a32f0n00.xes')
	log = xes_importer.import_from_file_xes('C:\\receipt.xes')

	"""for trace in log:
		for event in trace:
			event["newClassifier"] = event["concept:name"] + "+complete"""

	net, marking = inductive_factory.apply(log)
	petri_exporter.export_petri_to_pnml(net, marking, "receipt.pnml")
	#net, marking = petri_importer.import_petri_from_pnml("receipt.pnml")
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

	#results = align.versions.state_equation_classic.apply_log(log, net, marking, final_marking)
	#print(results)

	if True:
		fitTraces = []
		[traceIsFit, traceFitnessValue, activatedTransitions, placeFitness, reachedMarkings, enabledTransitionsInMarkings] = token_replay.apply_log(log, net, marking,
																									 final_marking,
																									 enable_placeFitness=True)
		i = 0
		while i < len(log):
			try:
				print("\n",i,[x["concept:name"] for x in log[i]])
				cfResult = align.versions.state_equation_a_star.apply_trace(log[i], net, marking, final_marking)['alignment']
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
			except:
				print("EXCEPTION ",i)
				traceback.print_exc()
			i = i + 1
		print(fitTraces)
		print(len(fitTraces))
from pm4py.algo.imdf.inductMinDirFollows import InductMinDirFollows as InductMinDirFollows
from pm4py.log.importer import xes as xes_importer
from pm4py.models.petri import visualize as pn_viz
from pm4py.algo.alignments import state_equation_classic
from pm4py.models import petri
from pm4py.algo.tokenreplay import token_replay

log = xes_importer.import_from_path_xes('C:\\running-example.xes')
imdf = InductMinDirFollows()
net, marking = imdf.apply(log)
for place in marking:
	print("initial marking "+place.name)
final_marking = petri.net.Marking()
for p in net.places:
    if not p.out_arcs:
        final_marking[p] = 1
for place in final_marking:
	print("final marking "+place.name)
[traceIsFit, traceFitnessValue] = token_replay.apply_log(log, net, marking, final_marking)
print("traceIsFit="+str(traceIsFit))
print("traceFitnessValue="+str(traceFitnessValue))
from pm4py.algo.petrigenerator import generator as petri_generator
from pm4py.models.petri import visualize as pn_viz
from pm4py.models.petri import exporter as petri_exporter
from pm4py.algo.playout import playout
from pm4py.algo.tokenreplay import token_replay
from pm4py.algo.imdf import inductMinDirFollows
from pm4py.models import petri

net, marking, final_marking = petri_generator.generate_petri()
petri_exporter.export_petri_to_pnml(net, marking, "generatedNet.pnml")
log = playout.playoutPetriNet(net, marking)
net2, marking2 = inductMinDirFollows.apply(log)
gviz = pn_viz.graphviz_visualization(net2)
gviz.view()
[traceIsFit, traceFitnessValue, activatedTransitions, placeFitness, reachedMarkings, enabledTransitionsInMarkings] = token_replay.apply_log(log, net, marking, final_marking)
fitTraces1 = [x for x in traceIsFit if x]
fitness1 = float(len(fitTraces1))/float(len(log))
print("fitness1 = "+str(fitness1))
final_marking2 = petri.net.Marking()
for p in net2.places:
    if not p.out_arcs:
        final_marking2[p] = 1
[traceIsFit, traceFitnessValue, activatedTransitions, placeFitness, reachedMarkings, enabledTransitionsInMarkings] = token_replay.apply_log(log, net2, marking2, final_marking2)
fitTraces2 = [x for x in traceIsFit if x]
fitness2 = float(len(fitTraces2))/float(len(log))
print("fitness2 = "+str(fitness2))
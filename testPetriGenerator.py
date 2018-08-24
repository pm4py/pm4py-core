from pm4py.algo.petrigenerator import generator as petri_generator
from pm4py.models.petri.exporter import pnml as petri_exporter
from pm4py.algo.playout import playout
from pm4py.algo.tokenreplay import token_replay

net, marking, final_marking = petri_generator.generate_petri()
petri_exporter.export_petri_to_pnml(net, marking, "generatedNet.pnml")
log = playout.playoutPetriNet(net, marking)
print([x["concept:name"] for x in log[0]])
[traceIsFit, traceFitnessValue, activatedTransitions, placeFitness, reachedMarkings, enabledTransitionsInMarkings] = token_replay.apply_log(log, net, marking, final_marking, enable_placeFitness=True, consider_remaining_in_fitness=True)
fitTraces1 = [x for x in traceIsFit if x]
fitness1 = float(len(fitTraces1))/float(len(log))
print("fitness1 = "+str(fitness1))
print("underfed places: ",[place.name for place in placeFitness.keys() if len(placeFitness[place]['underfedTraces']) > 0])
print("overfed places: ",[place.name for place in placeFitness.keys() if len(placeFitness[place]['overfedTraces']) > 0])
"""net2, marking2 = inductMinDirFollows.apply(log)
final_marking2 = petri.net.Marking()
for p in net2.places:
    if not p.out_arcs:
        final_marking2[p] = 1
[traceIsFit, traceFitnessValue, activatedTransitions, placeFitness, reachedMarkings, enabledTransitionsInMarkings] = token_replay.apply_log(log, net2, marking2, final_marking2, enable_placeFitness=True, consider_remaining_in_fitness=True)
fitTraces2 = [x for x in traceIsFit if x]
fitness2 = float(len(fitTraces2))/float(len(log))
print("fitness2 = "+str(fitness2))
print("underfed places: ",[place.name for place in placeFitness.keys() if len(placeFitness[place]['underfedTraces']) > 0])
print("overfed places: ",[place.name for place in placeFitness.keys() if len(placeFitness[place]['overfedTraces']) > 0])
gviz = pn_viz.graphviz_visualization(net2)
gviz.view()"""
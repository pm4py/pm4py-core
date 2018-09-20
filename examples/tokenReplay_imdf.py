import os, sys, inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from pm4py.algo.discovery.inductive import factory as inductive_factory
from pm4py.entities.log.importer.xes import factory as xes_importer
from pm4py.visualization.petrinet.common import visualize as pn_viz
from pm4py.algo.conformance.tokenreplay.versions import token_replay
import time

def execute_script():
    logPath = "..\\tests\\inputData\\running-example.xes"
    log = xes_importer.import_log(logPath)
    print("loaded log")
    net, marking, final_marking = inductive_factory.apply(log)
    for place in marking:
        print("initial marking " + place.name)
    for place in final_marking:
        print("final marking " + place.name)
    gviz = pn_viz.graphviz_visualization(net, initial_marking=marking, final_marking=final_marking, debug=True)
    gviz.view()
    time0 = time.time()
    print("started token replay")
    aligned_traces = token_replay.apply(log, net, marking, final_marking)
    fit_traces = [x for x in aligned_traces if x['tFit']]
    perc_fitness = 0.00
    if len(aligned_traces) > 0:
        perc_fitness = len(fit_traces) / len(aligned_traces)
    print("perc_fitness=", perc_fitness)

if __name__ == "__main__":
    execute_script()

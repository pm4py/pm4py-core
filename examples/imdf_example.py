import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
import os, sys, inspect
import pm4py
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
# from pm4py.algo.inductive.versions import dfg_only
from pm4py.algo.discovery.inductive import factory as inductive_factory
from pm4py.entities.log.importer.xes import factory as xes_importer
from pm4py.visualization.petrinet import factory as pn_vis_factory
import traceback

def execute_script():
    logPath = os.path.join("..","tests","inputData","running-example.xes")

    log = xes_importer.import_log(logPath)

    net, marking, final_marking = inductive_factory.apply(log)
    for place in marking:
        print("initial marking " + place.name)
    for place in final_marking:
        print("final marking " + place.name)
    gviz = pn_vis_factory.apply(net, marking, final_marking, parameters={"format": "svg", "debug": True})
    pn_vis_factory.view(gviz)

    if True:
        fitTraces = []

        i = 0
        while i < len(log):
            try:
                print("\n", i, [x["concept:name"] for x in log[i]])
                cfResult = pm4py.algo.conformance.alignments.versions.state_equation_a_star.apply(log[i], net, marking, final_marking)['alignment']
                if cfResult is None:
                    print("alignment is none!")
                else:
                    isFit = True
                    for couple in cfResult:
                        print(couple)
                        if not (couple[0] == couple[1] or couple[0] == ">>" and couple[1] == None):
                            isFit = False
                    print("isFit = " + str(isFit))

                    if isFit:
                        fitTraces.append(log[i])
            except:
                print("EXCEPTION ", i)
                traceback.print_exc()
            i = i + 1
        print(fitTraces)
        print(len(fitTraces))

if __name__ == "__main__":
    execute_script()
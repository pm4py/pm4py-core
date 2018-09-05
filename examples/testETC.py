import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from pm4py.evaluation.precision import factory as etc_factory
from pm4py.log.importer import xes as xes_importer
from pm4py.algo.inductive.versions import dfg_only
from pm4py.models import petri

log = xes_importer.import_from_file_xes('..\\tests\\inputData\\running-example.xes')
net, marking, final_marking = dfg_only.apply(log, None)
#petri_exporter.export_petri_to_pnml(net, marking, "running-example.pnml")
final_marking = petri.petrinet.Marking()

for p in net.places:
    if not p.out_arcs:
        final_marking[p] = 1
precision = etc_factory.apply(log, net, marking, final_marking)
print("precision=",precision)
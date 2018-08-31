from pm4py.algo.etconformance.versions import token_based
from pm4py.algo.etconformance import factory as etc_factory
from pm4py.log.importer import xes as xes_importer
from pm4py.algo.inductive.versions import dfg_only
from pm4py.models.petri.exporter import pnml as petri_exporter
from pm4py.models import petri

log = xes_importer.import_from_file_xes('C:\\running-example.xes')
net, marking, final_marking = dfg_only.apply(log, None)
petri_exporter.export_petri_to_pnml(net, marking, "running-example.pnml")
final_marking = petri.petrinet.Marking()

for p in net.places:
    if not p.out_arcs:
        final_marking[p] = 1
precision = etc_factory.apply(log, net, marking, final_marking)
print("precision=",precision)
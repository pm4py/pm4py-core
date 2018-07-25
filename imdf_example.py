from pm4py.algo.imdf.inductMinDirFollows import InductMinDirFollows as InductMinDirFollows
from pm4py.log.importer import xes as xes_importer
from pm4py.models.petri import visualize as pn_viz
from pm4py.algo.alignments import state_equation_classic
from pm4py.models import petri

log = xes_importer.import_from_path_xes('C:\\teleclaims.xes')
imdf = InductMinDirFollows()
net, marking = imdf.apply(log)
final_marking = petri.net.Marking()
for p in net.places:
    if not p.out_arcs:
        final_marking[p] = 1
#print(final_marking)
gviz = pn_viz.graphviz_visualization(net)
gviz.view()
"""log = [log[0]]
cfResult = state_equation_classic.apply_log(log, net, marking, final_marking)
for trAlign in cfResult:
	for couple in trAlign:
		print(couple.label)"""
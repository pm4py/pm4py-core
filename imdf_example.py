from pm4py.algo.imdf.inductMinDirFollows import InductMinDirFollows as InductMinDirFollows
from pm4py.log.importer import xes as xes_importer
from pm4py.models.petri import visualize as pn_viz
from pm4py.algo.alignments import state_equation_classic
from pm4py.models import petri
import traceback

log = xes_importer.import_from_path_xes('C:\\teleclaims.xes')
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
gviz = pn_viz.graphviz_visualization(net)
gviz.view()
print([x["concept:name"] for x in log[0]])
fitTraces = []
i = 0
while i < len(log):
	try:
		print(i)
		cfResult = state_equation_classic.apply_log([log[i]], net, marking, final_marking)
		isFit = True
		for couple in cfResult[0]:
			print(couple.label)
			if not (couple.label[0] == couple.label[1] or couple.label[0] == ">>" and couple.label[1] == None):
				isFit = False
				#break
		print("isFit = "+str(isFit))
		if isFit:
			fitTraces.append(log[i])
	except:
		print("EXCEPTION ",i)
		traceback.print_exc()
	i = i + 1
print(fitTraces)
print(len(fitTraces))
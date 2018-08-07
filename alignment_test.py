import pm4py.log.importer as log_import
import pm4py.models.petri as petri
import pm4py.algo.alignments as align
import cProfile
import pm4py.algo.imdf.inductMinDirFollows as imdf

#log = log_import.xes.import_from_path_xes('C:/Users/bas/Desktop/reviewing.xes')
# log = log_import.xes.import_from_path_xes('C:/Users/bas/Documents/tue/svn/private/logs/a32_logs/a32f0n00.xes')
log = log_import.xes.import_from_path_xes('C:/Users/bas/Documents/tue/svn/private/logs/a32_logs/a32f0n05.xes')
#net, marking = petri.importer.import_petri_from_pnml('C:/Users/bas/Desktop/reviewingPnml2.pnml')
net, marking = petri.importer.import_petri_from_pnml('C:/Users/bas/Desktop/a32.pnml')
# net, imarking = imdf.apply(log)
# viz = petri.visualize.graphviz_visualization(net)
# viz.view()
fmarking = petri.net.Marking()
for p in net.places:
    if len(p.out_arcs) == 0:
        fmarking[p] = 1

alignments = align.state_equation_classic.apply_log(log, net, marking, fmarking)
for a in alignments:
    print(a)


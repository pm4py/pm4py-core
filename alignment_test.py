import pm4py.models.petri as petri
import pm4py.algo.alignments as align
from pm4py import log as log_lib

if __name__=='__main__':
    #log = log_lib.importing.xes.import_from_path_xes('C:/Users/bas/Desktop/reviewing.xes')
    log = log_lib.importing.xes.import_from_path_xes('C:/Users/bas/Documents/tue/svn/private/logs/a32_logs/a32f0n05.xes')
    #net, marking = petri.importing.import_petri_from_pnml('C:/Users/bas/Desktop/reviewingPnml2.pnml')
    net, marking = petri.importing.pnml.import_petri_from_pnml('C:/Users/bas/Desktop/a32.pnml')
    # net, imarking = inductive.apply(log)
    # viz = petri.visualize.graphviz_visualization(net)
    # viz.view()
    fmarking = petri.net.Marking()
    for p in net.places:
        if len(p.out_arcs) == 0:
            fmarking[p] = 1

    alignments = align.versions.state_equation_a_star.apply_log(log, net, marking, fmarking)
    for a in alignments:
        if a['fitness'] < 1.0:
            print(a)


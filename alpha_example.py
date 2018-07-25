from pm4py.algo.alpha import classic as alpha_classic
from pm4py.log.importer import xes as xes_importer
from pm4py.models import petri
from pm4py.algo.alignments import state_equation_classic

log = xes_importer.import_from_path_xes('C:/Users/bas/Documents/tue/svn/private/logs/a12_logs/a12f0n00.xes')
net, marking = alpha_classic.apply(log)

log = xes_importer.import_from_path_xes('C:/Users/bas/Documents/tue/svn/private/logs/a12_logs/a12f0n05.xes')


final_marking = petri.net.Marking()
for p in net.places:
    if not p.out_arcs:
        final_marking[p] = 1

state_equation_classic.apply_log(log, net, marking, final_marking)


#gviz = pn_viz.graphviz_visualization(net)
#gviz.view()

#(sn, snm) = synchronous_product.construct(net, marking, log[0], '>>')
#gviz = pn_viz.graphviz_visualization(sn)
#gviz.view()


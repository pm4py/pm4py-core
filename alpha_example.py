from pm4py.algo.alpha import classic as alpha_classic
from pm4py.log.importer import xes as xes_importer
from pm4py.models.petri import visualize as pn_viz

log = xes_importer.import_from_path_xes('C:/Users/bas/Documents/tue/svn/private/logs/a22_logs/a22f0n00.xes')
net = alpha_classic.apply(log)
gviz = pn_viz.graphviz_visualization(net)
gviz.view()


from pm4py.algo.imdf.inductMinDirFollows import InductMinDirFollows as InductMinDirFollows
from pm4py.log.importer import xes as xes_importer
from pm4py.models.petri import visualize as pn_viz

log = xes_importer.import_from_path_xes('C:\\roadtraffic.xes')
imdf = InductMinDirFollows()
net = imdf.apply(log)
gviz = pn_viz.graphviz_visualization(net)
gviz.view()


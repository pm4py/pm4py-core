from pm4py.algo.imdf.inductMinDirFollows import InductMinDirFollows as InductMinDirFollows
from pm4py.log.importer import xes as xes_importer
from pm4py.models.petri import visualize as pn_viz
from pm4py.algo.alignments.versions import state_equation_classic
from pm4py.models import petri
import traceback

log = xes_importer.import_from_path_xes('C:\\reviewing.xes')
imdf = InductMinDirFollows()
net = imdf.apply(log)
gviz = pn_viz.graphviz_visualization(net)
gviz.view()


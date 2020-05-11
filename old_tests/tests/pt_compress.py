from pm4py.visualization.process_tree import factory as pt_viz
from pm4py.algo.simulation.tree_generator import factory as pt_gen
from pm4py.objects.process_tree import util as pt_util
from pm4py.objects.conversion.process_tree import factory as pt_conv
from pm4py.visualization.petrinet import factory as pn_viz
from pm4py.objects.petri import utils as pn_util
import time


if __name__ == "__main__":
    pt = pt_gen.apply()
    pt_viz.view(pt_viz.apply(pt, parameters={"format": "svg"}))
    time.sleep(1)
    pn, im, fm = pt_conv.apply(pt)
    pn_viz.view(pn_viz.apply(pn, parameters={'format': 'svg'}))
    time.sleep(1)
    pt = pt_util.fold(pt)
    pt_viz.view(pt_viz.apply(pt, parameters={"format": "svg"}))
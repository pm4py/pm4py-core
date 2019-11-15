from pm4py.algo.simulation.tree_generator import factory as pt_gen
from pm4py.objects.conversion.process_tree import factory as pt_conv
from pm4py.visualization.petrinet import factory as pn_viz
from pm4py.visualization.process_tree import factory as pt_viz
from pm4py.objects.process_tree import util as pt_util
from pm4py.objects.petri import utils as pn_util
import time
from pm4py.objects.petri.exporter import factory as pn_exp


if __name__ == '__main__':
    pt = pt_gen.apply()
    gviz = pt_viz.apply(pt, parameters={'format': 'svg'})
    pt_viz.view(gviz)
    time.sleep(1)
    pt = pt_util.fold(pt)
    gviz = pt_viz.apply(pt, parameters={'format': 'svg'})
    pt_viz.view(gviz)
    time.sleep(1)
    pn, ini, fin = pt_conv.apply(pt)
    gviz = pn_viz.apply(pn, ini, fin, parameters={"format": "svg"})
    pn_viz.view(gviz)
    time.sleep(1)
    pn_exp.apply(pn, ini, 'C:/Users/zelst/Desktop/translation_test.pnml', final_marking=fin)

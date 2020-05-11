import os

from pm4py.algo.discovery.dfg import algorithm as dfg_algorithm
from pm4py.objects.conversion.dfg import converter as dfg_conv
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.visualization.dfg import visualizer as dfg_vis_fact
from pm4py.visualization.petrinet import visualizer as pn_vis


def execute_script():
    log_path = os.path.join("..","tests", "input_data", "running-example.xes")
    log = xes_importer.apply(log_path)
    dfg = dfg_algorithm.apply(log)
    dfg_gv = dfg_vis_fact.apply(dfg, log, parameters={dfg_vis_fact.Variants.FREQUENCY.value.Parameters.FORMAT: "svg"})
    dfg_vis_fact.view(dfg_gv)
    net, im, fm = dfg_conv.apply(dfg)
    gviz = pn_vis.apply(net, im, fm, parameters={pn_vis.Variants.WO_DECORATION.value.Parameters.FORMAT: "svg"})
    pn_vis.view(gviz)


if __name__ == "__main__":
    execute_script()

import os

from pm4py.algo.discovery.dfg import factory as dfg_factory
from pm4py.objects.conversion.dfg import factory as dfg_conv_factory
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.visualization.dfg import factory as dfg_vis_fact
from pm4py.visualization.petrinet import factory as pn_vis_factory


def execute_script():
    log_path = os.path.join("..","tests", "input_data", "running-example.xes")
    log = xes_importer.apply(log_path)
    dfg = dfg_factory.apply(log)
    dfg_gv = dfg_vis_fact.apply(dfg, log, parameters={"format": "svg"})
    dfg_vis_fact.view(dfg_gv)
    net, im, fm = dfg_conv_factory.apply(dfg)
    gviz = pn_vis_factory.apply(net, im, fm, parameters={"format": "svg"})
    pn_vis_factory.view(gviz)

if __name__ == "__main__":
    execute_script()
import os

from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.algo.enhancement.sna import factory as sna_factory
from pm4py.visualization.sna import factory as pn_vis_factory


def execute_script():
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))

    hw_values = sna_factory.apply(log, variant="handover")
    wt_values = sna_factory.apply(log, variant="working_together")
    sub_values = sna_factory.apply(log, variant="subcontracting")
    ja_values = sna_factory.apply(log, variant="jointactivities")

    gviz_sub = pn_vis_factory.apply(sub_values, variant="networkx", parameters={"format": "svg"})
    gviz_hw = pn_vis_factory.apply(hw_values, variant="pyvis")
    gviz_wt = pn_vis_factory.apply(wt_values, variant="networkx", parameters={"format": "svg"})
    gviz_ja = pn_vis_factory.apply(ja_values, variant="pyvis")

    pn_vis_factory.view(gviz_sub, variant="networkx")
    pn_vis_factory.view(gviz_hw, variant="pyvis")
    pn_vis_factory.view(gviz_wt, variant="networkx")
    pn_vis_factory.view(gviz_ja, variant="pyvis")


if __name__ == "__main__":
    execute_script()
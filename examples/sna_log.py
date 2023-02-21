import os

from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.organizational_mining.sna import algorithm as sna_algorithm
from pm4py.visualization.sna import visualizer as pn_vis


def execute_script():
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))

    hw_values = sna_algorithm.apply(log, variant=sna_algorithm.Variants.HANDOVER_LOG)
    wt_values = sna_algorithm.apply(log, variant=sna_algorithm.Variants.WORKING_TOGETHER_LOG)
    sub_values = sna_algorithm.apply(log, variant=sna_algorithm.Variants.SUBCONTRACTING_LOG)
    ja_values = sna_algorithm.apply(log, variant=sna_algorithm.Variants.JOINTACTIVITIES_LOG)

    gviz_sub = pn_vis.apply(sub_values, variant=pn_vis.Variants.NETWORKX,
                            parameters={pn_vis.Variants.NETWORKX.value.Parameters.FORMAT: "svg"})
    gviz_hw = pn_vis.apply(hw_values, variant=pn_vis.Variants.PYVIS)
    gviz_wt = pn_vis.apply(wt_values, variant=pn_vis.Variants.NETWORKX,
                           parameters={pn_vis.Variants.NETWORKX.value.Parameters.FORMAT: "svg"})
    gviz_ja = pn_vis.apply(ja_values, variant=pn_vis.Variants.PYVIS)

    pn_vis.view(gviz_sub, variant=pn_vis.Variants.NETWORKX)
    pn_vis.view(gviz_hw, variant=pn_vis.Variants.PYVIS)
    pn_vis.view(gviz_wt, variant=pn_vis.Variants.NETWORKX)
    pn_vis.view(gviz_ja, variant=pn_vis.Variants.PYVIS)


if __name__ == "__main__":
    execute_script()

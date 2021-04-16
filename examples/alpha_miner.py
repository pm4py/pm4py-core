import os

from pm4py.objects.log.importer.xes import importer as xes_import
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.visualization.petri_net import visualizer as pn_vis


def execute_script():
    log_path = os.path.join("..", "tests", "input_data", "running-example.xes")
    log = xes_import.apply(log_path)

    net, i_m, f_m = alpha_miner.apply(log)

    gviz = pn_vis.apply(net, i_m, f_m,
                        parameters={pn_vis.Variants.WO_DECORATION.value.Parameters.FORMAT: "svg",
                                    pn_vis.Variants.WO_DECORATION.value.Parameters.DEBUG: False})
    pn_vis.view(gviz)


if __name__ == "__main__":
    execute_script()

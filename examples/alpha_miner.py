import os

from pm4py.objects.log.importer.xes import factory as xes_import
from pm4py.algo.discovery.alpha import factory as alpha_miner


def execute_script():
    log_path = os.path.join("..", "tests", "input_data", "running-example.xes")
    log = xes_import.apply(log_path)

    net, iM, fM = alpha_miner.apply(log)
    from pm4py.visualization.petrinet import factory as pn_vis_factory
    gviz = pn_vis_factory.apply(net, iM, fM, parameters={"format": "svg", "debug": True})
    pn_vis_factory.view(gviz)


if __name__ == "__main__":
    execute_script()
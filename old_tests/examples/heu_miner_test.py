import os

from pm4py.algo.discovery.heuristics import factory as heuristics_miner
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.visualization.heuristics_net import factory as hn_vis_factory
from pm4py.visualization.petrinet import factory as petri_vis_factory


def execute_script():
    log = xes_importer.apply(os.path.join("..", "tests", "compressed_input_data", "09_a32f0n00.xes.gz"))
    heu_net = heuristics_miner.apply_heu(log, parameters={"dependency_thresh": 0.99})
    gviz = hn_vis_factory.apply(heu_net, parameters={"format": "svg"})
    hn_vis_factory.view(gviz)
    net, im, fm = heuristics_miner.apply(log, parameters={"dependency_thresh": 0.99})
    gviz2 = petri_vis_factory.apply(net, im, fm, parameters={"format": "svg"})
    petri_vis_factory.view(gviz2)


if __name__ == "__main__":
    execute_script()

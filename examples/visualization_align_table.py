import os
from pm4py.objects.log.importer.xes import importer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.conformance.alignments.petri_net import algorithm as alignments
from pm4py.visualization.align_table import visualizer


def execute_script():
    log = importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
    net, im, fm = inductive_miner.apply(log)
    aligned_traces = alignments.apply(log, net, im, fm)
    gviz = visualizer.apply(log, aligned_traces,
                            parameters={visualizer.Variants.CLASSIC.value.Parameters.FORMAT: "svg"})
    visualizer.view(gviz)


if __name__ == "__main__":
    execute_script()

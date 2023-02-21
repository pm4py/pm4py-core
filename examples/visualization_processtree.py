from pm4py.objects.log.importer.xes import importer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.visualization.process_tree import visualizer as pt_vis_factory
from pm4py.visualization.process_tree import visualizer as pt_visualizer
import os


def execute_script():
    log = importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
    tree = inductive_miner.apply(log)
    gviz1 = pt_vis_factory.apply(tree, parameters={"format": "svg"})
    # pt_vis_factory.view(gviz1)
    gviz2 = pt_visualizer.apply(tree, parameters={pt_visualizer.Variants.WO_DECORATION.value.Parameters.FORMAT: "svg"})
    pt_visualizer.view(gviz2)


if __name__ == "__main__":
    execute_script()

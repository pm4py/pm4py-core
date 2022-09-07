from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.decision_mining import algorithm
from pm4py.visualization.decisiontree import visualizer as visualizer
from pm4py.objects.conversion.process_tree import converter as process_tree_converter
import os


def execute_script():
    # in this case, we obtain a decision tree by alignments on a specific decision point
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
    process_tree = inductive_miner.apply(log)
    net, im, fm = process_tree_converter.apply(process_tree)
    # we need to specify a decision point. In this case, the place p_10 is a suitable decision point
    clf, feature_names, classes = algorithm.get_decision_tree(log, net, im, fm, decision_point="p_10")
    # we can visualize the decision tree
    gviz = visualizer.apply(clf, feature_names, classes,
                            parameters={visualizer.Variants.CLASSIC.value.Parameters.FORMAT: "svg"})
    visualizer.view(gviz)


if __name__ == "__main__":
    execute_script()

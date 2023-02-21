import os

from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.visualization.petri_net import visualizer as pn_vis
from pm4py.objects.conversion.process_tree import converter as process_tree_converter


def execute_script():
    # import the log
    log_path = os.path.join("..", "tests", "input_data", "receipt.xes")
    log = xes_importer.apply(log_path)
    # apply Inductive Miner
    process_tree = inductive_miner.apply(log)
    net, initial_marking, final_marking = process_tree_converter.apply(process_tree)
    # get visualization
    variant = pn_vis.Variants.PERFORMANCE
    parameters_viz = {pn_vis.Variants.PERFORMANCE.value.Parameters.AGGREGATION_MEASURE: "mean", pn_vis.Variants.PERFORMANCE.value.Parameters.FORMAT: "svg"}
    gviz = pn_vis.apply(net, initial_marking, final_marking, log=log, variant=variant,
                        parameters=parameters_viz)
    pn_vis.view(gviz)
    # do another visualization with frequency
    variant = pn_vis.Variants.FREQUENCY
    parameters_viz = {pn_vis.Variants.FREQUENCY.value.Parameters.FORMAT: "svg"}
    gviz = pn_vis.apply(net, initial_marking, final_marking, log=log, variant=variant,
                        parameters=parameters_viz)
    pn_vis.view(gviz)


if __name__ == "__main__":
    execute_script()

import os

from pm4py.algo.discovery.inductive import factory as inductive_miner
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.visualization.petrinet import factory as pn_vis_factory


def execute_script():
    # import the log
    log_path = os.path.join("..", "tests", "input_data", "receipt.xes")
    log = xes_importer.import_log(log_path)
    # apply Inductive Miner
    net, initial_marking, final_marking = inductive_miner.apply(log)
    # get visualization
    variant = "performance"
    parameters_viz = {"aggregationMeasure": "mean", "format": "svg"}
    gviz = pn_vis_factory.apply(net, initial_marking, final_marking, log=log, variant=variant,
                                parameters=parameters_viz)
    pn_vis_factory.view(gviz)


if __name__ == "__main__":
    execute_script()

import os

from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.evaluation import algorithm as general_evaluation
from pm4py.objects.log.importer.xes import importer as xes_importer


def execute_script():
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "reviewing.xes"))
    net, marking, final_marking = inductive_miner.apply(log)
    metrics = general_evaluation.apply(log, net, marking, final_marking)
    print("metrics=", metrics)


if __name__ == "__main__":
    execute_script()

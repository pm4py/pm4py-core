from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.simulation.playout.process_tree import algorithm as tree_playout
import os


def execute_script():
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
    tree = inductive_miner.apply(log)
    new_log_1 = tree_playout.apply(tree)
    print(len(new_log_1))
    new_tree_1 = inductive_miner.apply(new_log_1)
    print(new_tree_1)
    new_log_2 = tree_playout.apply(tree, variant=tree_playout.Variants.EXTENSIVE)
    print(len(new_log_2))
    new_tree_2 = inductive_miner.apply(new_log_2)
    print(new_tree_2)


if __name__ == "__main__":
    execute_script()

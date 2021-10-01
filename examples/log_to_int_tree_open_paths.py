import pm4py
import os
from pm4py.algo.transformation.log_to_interval_tree import algorithm as log_to_interval_tree


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "receipt.xes"))
    tree = log_to_interval_tree.apply(log, variant=log_to_interval_tree.Variants.OPEN_PATHS)
    # see how many paths are open at the timestamp 1319616410
    print(len(tree[1319616410]))
    # read the detailed information about the source and target event of each path
    print(tree[1319616410])


if __name__ == "__main__":
    execute_script()

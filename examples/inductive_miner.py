import pm4py
import os
from examples import examples_conf



def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "running-example.xes"))
    tree = pm4py.discover_process_tree_inductive(log, noise_threshold=0.2)
    pm4py.view_process_tree(tree, format=examples_conf.TARGET_IMG_FORMAT)
    net, im, fm = pm4py.convert_to_petri_net(tree)
    pm4py.view_petri_net(net, im, fm, format=examples_conf.TARGET_IMG_FORMAT)


if __name__ == "__main__":
    execute_script()

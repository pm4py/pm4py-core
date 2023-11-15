import os

import pm4py
from pm4py.algo.transformation import log_to_trie
from pm4py.visualization.trie import visualizer
from examples import examples_conf



def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "running-example.xes"))
    trie = log_to_trie.algorithm.apply(log)
    gviz = visualizer.apply(trie, parameters={"format": examples_conf.TARGET_IMG_FORMAT})
    visualizer.view(gviz)


if __name__ == "__main__":
    execute_script()

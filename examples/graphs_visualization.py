import os

import pm4py
from examples import examples_conf


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "receipt.xes"))

    # visualize case duration graph
    pm4py.view_case_duration_graph(log, format=examples_conf.TARGET_IMG_FORMAT)

    # visualize events over time graph
    pm4py.view_events_per_time_graph(log, format=examples_conf.TARGET_IMG_FORMAT)


if __name__ == "__main__":
    execute_script()

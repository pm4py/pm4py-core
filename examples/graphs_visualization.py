import os

import pm4py


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "receipt.xes"))

    # visualize case duration graph
    pm4py.view_case_duration_graph(log, format="svg")

    # visualize events over time graph
    pm4py.view_events_per_time_graph(log, format="svg")


if __name__ == "__main__":
    execute_script()

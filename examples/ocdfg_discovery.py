import pm4py
import os


def execute_script():
    ocel = pm4py.read_ocel(os.path.join("..", "tests", "input_data", "ocel", "example_log.jsonocel"))
    ocdfg = pm4py.discover_ocdfg(ocel)
    # views the model with the frequency annotation
    pm4py.view_ocdfg(ocdfg, format="svg")
    # views the model with the performance annotation
    pm4py.view_ocdfg(ocdfg, format="svg", annotation="performance", performance_aggregation="median")


if __name__ == "__main__":
    execute_script()

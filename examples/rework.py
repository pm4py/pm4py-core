import pm4py
import os
from pm4py.statistics.rework.log import get as rework_get


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "receipt.xes"))
    rework = rework_get.apply(log)
    print(rework)


if __name__ == "__main__":
    execute_script()

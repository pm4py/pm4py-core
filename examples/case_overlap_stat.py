import pm4py
import os
from pm4py.statistics.traces.case_overlap.log import get as wip_get


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "receipt.xes"))
    # calculates the WIP statistics from the event log object.
    # The WIP statistic associates to each case the number of cases open during the lifecycle of the case
    wip = wip_get.apply(log)
    print(wip)


if __name__ == "__main__":
    execute_script()

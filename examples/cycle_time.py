import os

import pm4py
from pm4py.statistics.traces.cycle_time.log import get as cycle_time_get


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "interval_event_log.xes"))
    print(cycle_time_get.apply(log, parameters={cycle_time_get.Parameters.START_TIMESTAMP_KEY: "start_timestamp",
                                                cycle_time_get.Parameters.TIMESTAMP_KEY: "time:timestamp"}))


if __name__ == "__main__":
    execute_script()

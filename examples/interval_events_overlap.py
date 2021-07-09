import pm4py
from pm4py.statistics.overlap.interval_events.log import get as interval_events_overlap
import os


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "interval_event_log.xes"))
    # gets the overlap of each interval event with the other events of the log
    overlap = interval_events_overlap.apply(log, parameters={
        interval_events_overlap.Parameters.START_TIMESTAMP_KEY: "start_timestamp"})
    # print the overlap for all the events
    print(overlap)
    # print the number of intersections of the event having max overlap
    print(max(overlap))


if __name__ == "__main__":
    execute_script()

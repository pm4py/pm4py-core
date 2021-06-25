import pm4py
from pm4py.algo.discovery.batches import algorithm
import os


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "receipt.xes"))
    # detect the batches from the event log
    batches = algorithm.apply(log)
    # print the batches (complete information) in a single row
    print(batches)
    # print a summary information (size) for each activity-resource combination that is performed in batches
    for batch in batches:
        print(batch[0], batch[1])


if __name__ == "__main__":
    execute_script()

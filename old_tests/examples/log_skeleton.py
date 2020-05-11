from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.algo.discovery.log_skeleton import factory as lsk_factory
from pm4py.algo.conformance.log_skeleton import factory as lsk_conf_factory
import os


def execute_script():
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "receipt.xes"))
    # discovers the log skeleton with a minimal noise
    log_skeleton = lsk_factory.apply(log, parameters={"noise_threshold": 0.01})
    print(log_skeleton)
    # applies conformance checking to it
    results = lsk_conf_factory.apply(log, log_skeleton)
    for i in range(min(len(results), 5)):
        # print the i-the conformance checking
        print(results[i])


if __name__ == "__main__":
    execute_script()

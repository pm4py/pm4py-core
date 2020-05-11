from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.algo.discovery.inductive import factory as inductive_miner
from pm4py.algo.conformance.tokenreplay import factory as tr_factory
import os


def execute_script():
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
    net, im, fm = inductive_miner.apply(log)
    # perform the backwards token-based replay
    replayed_traces = tr_factory.apply(log, net, im, fm, variant="backwards")
    print(replayed_traces)


if __name__ == "__main__":
    execute_script()

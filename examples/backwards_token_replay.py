from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.conformance.tokenreplay import algorithm as tr
from pm4py.objects.conversion.process_tree import converter as process_tree_converter
import os


def execute_script():
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
    process_tree = inductive_miner.apply(log)
    net, im, fm = process_tree_converter.apply(process_tree)
    # perform the backwards token-based replay
    replayed_traces = tr.apply(log, net, im, fm, variant=tr.Variants.BACKWARDS)
    print(replayed_traces)


if __name__ == "__main__":
    execute_script()

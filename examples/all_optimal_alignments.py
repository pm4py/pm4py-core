import pm4py
from pm4py.algo.conformance.alignments.petri_net.variants import generator_dijkstra_less_memory
import os


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "running-example.xes"), return_legacy_log_object=True)

    net, im, fm = pm4py.discover_petri_net_inductive(log)

    for trace in log:
        print("\n\n")
        for ali in generator_dijkstra_less_memory.apply(trace, net, im, fm):
            print(ali)


if __name__ == "__main__":
    execute_script()

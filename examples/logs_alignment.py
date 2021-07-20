import time

import pm4py
from pm4py.algo.conformance.alignments.edit_distance import algorithm as logs_alignment
from pm4py.algo.evaluation.replay_fitness.variants import alignment_based
from pm4py.objects.process_tree.utils import bottomup as bottomup_discovery
from pm4py.algo.simulation.playout.process_tree import algorithm as tree_playout


def execute_script():
    # read an event log
    log = pm4py.read_xes("../tests/compressed_input_data/02_teleclaims.xes.gz")
    # log = pm4py.read_xes("../tests/input_data/receipt.xes")
    print("number of variants of the original log ->", len(pm4py.get_variants_as_tuples(log)))
    # discover a process model
    tree = pm4py.discover_process_tree_inductive(log)
    # simulate a log out of the model (to have another log that is similar to the original)
    aa = time.time()
    min_trace_length = bottomup_discovery.get_min_trace_length(tree)
    simulated_log = tree_playout.apply(tree, variant=tree_playout.Variants.EXTENSIVE,
                                       parameters={"max_trace_length": min_trace_length + 2})
    print("number of variants of the simulated log -> ", len(simulated_log))
    # apply the alignments between this log and the model
    bb = time.time()
    aligned_traces = logs_alignment.apply(log, simulated_log)
    cc = time.time()
    print(aligned_traces[0])
    print("playout time", bb - aa)
    print("alignments time", cc - bb)
    print("TOTAL", cc - aa)
    print(alignment_based.evaluate(aligned_traces))
    # apply the anti alignments between this log and the model
    dd = time.time()
    anti_aligned_traces = logs_alignment.apply(log, simulated_log,
                                               parameters={
                                                   logs_alignment.Variants.EDIT_DISTANCE.value.Parameters.PERFORM_ANTI_ALIGNMENT: True})
    ee = time.time()
    print(anti_aligned_traces[0])
    print("anti alignments time", ee - dd)
    print(alignment_based.evaluate(anti_aligned_traces))


if __name__ == "__main__":
    execute_script()

import pm4py
import os
from pm4py.algo.conformance.alignments.petri_net import algorithm as alignments
from pm4py.algo.conformance.alignments.petri_net.utils import log_enrichment
from pm4py.objects.log.importer.xes import importer as xes_importer


def execute_script():
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
    filtered_log = pm4py.filter_variants_top_k(log, 1)
    net, im, fm = pm4py.discover_petri_net_inductive(filtered_log)
    aligned_traces = alignments.apply(log, net, im, fm, parameters={"ret_tuple_as_trans_desc": True})
    enriched_log = log_enrichment.apply(log, aligned_traces)
    print(enriched_log)


if __name__ == "__main__":
    execute_script()

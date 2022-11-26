import unittest
import pm4py
from pm4py.algo.conformance.tokenreplay import algorithm as token_based_replay
from pm4py.algo.conformance.alignments.petri_net import algorithm as alignments
from pm4py.algo.discovery.log_skeleton import algorithm as log_skeleton_discovery
from pm4py.algo.conformance.log_skeleton import algorithm as log_skeleton_conformance
from pm4py.algo.discovery.footprints import algorithm as footprints_discovery
from pm4py.algo.conformance.footprints.variants import log_model, trace_extensive
from pm4py.objects.log.importer.xes import importer as xes_importer


class DiagnDfConfChecking(unittest.TestCase):
    def test_tbr_normal(self):
        log = xes_importer.apply("input_data/running-example.xes")
        net, im, fm = pm4py.discover_petri_net_inductive(log, noise_threshold=0.2)
        replayed_traces = token_based_replay.apply(log, net, im, fm)
        diagn_df = token_based_replay.get_diagnostics_dataframe(log, replayed_traces)

    def test_tbr_backwards(self):
        log = xes_importer.apply("input_data/running-example.xes")
        net, im, fm = pm4py.discover_petri_net_inductive(log, noise_threshold=0.2)
        replayed_traces = token_based_replay.apply(log, net, im, fm, variant=token_based_replay.Variants.BACKWARDS)
        diagn_df = token_based_replay.get_diagnostics_dataframe(log, replayed_traces, variant=token_based_replay.Variants.BACKWARDS)

    def test_align(self):
        log = xes_importer.apply("input_data/running-example.xes")
        net, im, fm = pm4py.discover_petri_net_inductive(log, noise_threshold=0.2)
        aligned_traces = alignments.apply(log, net, im, fm)
        diagn_df = alignments.get_diagnostics_dataframe(log, aligned_traces)

    def test_log_skeleton(self):
        log = xes_importer.apply("input_data/running-example.xes")
        log_skeleton = log_skeleton_discovery.apply(log, parameters={log_skeleton_discovery.Variants.CLASSIC.value.Parameters.NOISE_THRESHOLD: 0.05})
        conf_result = log_skeleton_conformance.apply(log, log_skeleton)
        diagn_df = log_skeleton_conformance.get_diagnostics_dataframe(log, conf_result)

    def test_footprints_classic(self):
        log = xes_importer.apply("input_data/running-example.xes")
        fp_log = footprints_discovery.apply(log, variant=footprints_discovery.Variants.TRACE_BY_TRACE)
        tree = pm4py.discover_process_tree_inductive(log, noise_threshold=0.2)
        fp_model = footprints_discovery.apply(tree)
        conf_result = log_model.apply(fp_log, fp_model)
        diagn_df = log_model.get_diagnostics_dataframe(log, conf_result)

    def test_footprints_extensive(self):
        log = xes_importer.apply("input_data/running-example.xes")
        fp_log = footprints_discovery.apply(log, variant=footprints_discovery.Variants.TRACE_BY_TRACE)
        tree = pm4py.discover_process_tree_inductive(log, noise_threshold=0.2)
        fp_model = footprints_discovery.apply(tree)
        conf_result = trace_extensive.apply(fp_log, fp_model)
        diagn_df = trace_extensive.get_diagnostics_dataframe(log, conf_result)


if __name__ == "__main__":
    unittest.main()

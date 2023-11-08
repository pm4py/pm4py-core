import os
import unittest

from pm4py.algo.conformance.alignments.petri_net import algorithm as align_alg
from pm4py.algo.discovery.alpha import algorithm as alpha_alg
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.objects import petri_net
from pm4py.objects.log.importer.xes import importer as xes_importer
from tests.constants import INPUT_DATA_DIR
from pm4py.objects.conversion.process_tree import converter as process_tree_converter


class AlignmentTest(unittest.TestCase):
    def test_alignment_alpha(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log = xes_importer.apply(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        net, marking, fmarking = alpha_alg.apply(log)
        final_marking = petri_net.obj.Marking()
        for p in net.places:
            if not p.out_arcs:
                final_marking[p] = 1
        for trace in log:
            cf_result = \
            align_alg.apply(trace, net, marking, final_marking, variant=align_alg.VERSION_DIJKSTRA_NO_HEURISTICS)[
                'alignment']
            is_fit = True
            for couple in cf_result:
                if not (couple[0] == couple[1] or couple[0] == ">>" and couple[1] is None):
                    is_fit = False
            if not is_fit:
                raise Exception("should be fit")

    def test_alignment_pnml(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log = xes_importer.apply(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        process_tree = inductive_miner.apply(log)
        net, marking, final_marking = process_tree_converter.apply(process_tree)
        for trace in log:
            cf_result = \
            align_alg.apply(trace, net, marking, final_marking, variant=align_alg.VERSION_DIJKSTRA_NO_HEURISTICS)[
                'alignment']
            is_fit = True
            for couple in cf_result:
                if not (couple[0] == couple[1] or couple[0] == ">>" and couple[1] is None):
                    is_fit = False
            if not is_fit:
                raise Exception("should be fit")

    def test_tree_align_receipt(self):
        import pm4py
        log = pm4py.read_xes("input_data/receipt.xes")
        tree = pm4py.discover_process_tree_inductive(log, noise_threshold=0.2)
        al = pm4py.conformance_diagnostics_alignments(log, tree, return_diagnostics_dataframe=False)

    def test_tree_align_reviewing(self):
        import pm4py
        log = pm4py.read_xes("compressed_input_data/04_reviewing.xes.gz")
        tree = pm4py.discover_process_tree_inductive(log, noise_threshold=0.2)
        al = pm4py.conformance_diagnostics_alignments(log, tree, return_diagnostics_dataframe=False)

    def test_tree_align_reviewing_classifier(self):
        import pm4py
        log = xes_importer.apply("compressed_input_data/04_reviewing.xes.gz")
        for trace in log:
            for event in trace:
                event["concept:name"] = event["concept:name"] + "+" + event["lifecycle:transition"]
        tree = pm4py.discover_process_tree_inductive(log, noise_threshold=0.2)
        al = pm4py.conformance_diagnostics_alignments(log, tree, return_diagnostics_dataframe=False)


    def test_tree_align_reviewing_classifier_different_key(self):
        import pm4py
        log = xes_importer.apply("compressed_input_data/04_reviewing.xes.gz")
        for trace in log:
            for event in trace:
                event["@@classifier"] = event["concept:name"] + "+" + event["lifecycle:transition"]
        from pm4py.algo.discovery.inductive import algorithm as inductive_miner
        tree = inductive_miner.apply(log, parameters={inductive_miner.Parameters.ACTIVITY_KEY: "@@classifier"})
        from pm4py.algo.conformance.alignments.process_tree.variants import search_graph_pt
        al = search_graph_pt.apply(log, tree, parameters={search_graph_pt.Parameters.ACTIVITY_KEY: "@@classifier"})

    def test_variant_state_eq_a_star(self):
        import pm4py
        log = pm4py.read_xes("input_data/running-example.xes")
        net, im, fm = pm4py.discover_petri_net_inductive(log)
        align_alg.apply(log, net, im, fm, variant=align_alg.Variants.VERSION_STATE_EQUATION_A_STAR)

    def test_variant_dijkstra_less_memory(self):
        import pm4py
        log = pm4py.read_xes("input_data/running-example.xes")
        net, im, fm = pm4py.discover_petri_net_inductive(log)
        align_alg.apply(log, net, im, fm, variant=align_alg.Variants.VERSION_DIJKSTRA_LESS_MEMORY)

    def test_variant_tweaked_state_eq_a_star(self):
        import pm4py
        log = pm4py.read_xes("input_data/running-example.xes")
        net, im, fm = pm4py.discover_petri_net_inductive(log)
        align_alg.apply(log, net, im, fm, variant=align_alg.Variants.VERSION_TWEAKED_STATE_EQUATION_A_STAR)



if __name__ == "__main__":
    unittest.main()

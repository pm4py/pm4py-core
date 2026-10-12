import os
import unittest
from datetime import datetime, timedelta, timezone

from pm4py.algo.conformance.alignments.petri_net import algorithm as align_alg
from pm4py.algo.discovery.alpha import algorithm as alpha_alg
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.objects import petri_net
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.obj import Event, EventLog, Trace
from pm4py.objects.process_tree.obj import Operator as ProcessTreeOperator, ProcessTree
from tests.constants import INPUT_DATA_DIR
from pm4py.objects.conversion.process_tree import converter as process_tree_converter
from config import test_config


class AlignmentTest(unittest.TestCase):
    @staticmethod
    def _loop_tree(*children):
        tree = ProcessTree(operator=ProcessTreeOperator.LOOP)
        tree.children = list(children)
        for child in children:
            child.parent = tree
        return tree

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
        log = xes_importer.apply("compressed_input_data/04_reviewing.xes.gz")
        for trace in log:
            for event in trace:
                event["@@classifier"] = event["concept:name"] + "+" + event["lifecycle:transition"]
        from pm4py.algo.discovery.inductive import algorithm as inductive_miner
        tree = inductive_miner.apply(log, parameters={inductive_miner.Parameters.ACTIVITY_KEY: "@@classifier"})
        from pm4py.algo.conformance.alignments.process_tree.variants import search_graph_pt
        al = search_graph_pt.apply(log, tree, parameters={search_graph_pt.Parameters.ACTIVITY_KEY: "@@classifier"})

    def test_tree_align3(self):
        log = xes_importer.apply("compressed_input_data/01_running-example.xes.gz")
        from pm4py.algo.discovery.inductive import algorithm as inductive_miner
        tree = inductive_miner.apply(log)
        from pm4py.algo.conformance.alignments.process_tree.variants import dynamic_programming
        al = dynamic_programming.apply(log, tree)

    def test_dynamic_tree_align_loop_starts_with_do_branch(self):
        from pm4py.algo.conformance.alignments.process_tree.variants import dynamic_programming

        tree = self._loop_tree(ProcessTree(label="A"), ProcessTree(label="B"))

        self.assertEqual(0, dynamic_programming.align_trace_with_process_tree(("A",), tree)[0])
        self.assertEqual(0, dynamic_programming.align_trace_with_process_tree(("A", "B", "A"), tree)[0])
        self.assertEqual(1, dynamic_programming.align_trace_with_process_tree(tuple(), tree)[0])
        self.assertEqual(1, dynamic_programming.align_trace_with_process_tree(("B", "A"), tree)[0])

    def test_dynamic_tree_align_loop_allows_empty_redo_alignment(self):
        from pm4py.algo.conformance.alignments.process_tree.variants import dynamic_programming

        tree = self._loop_tree(ProcessTree(label="A"), ProcessTree())

        self.assertEqual(0, dynamic_programming.align_trace_with_process_tree(("A", "A"), tree)[0])

    def test_tree_align3_mip(self):
        if test_config.IS_PIPELINE_RUN:
            self.skipTest("Skipping the test in pipelines since pulp can not be installed")
        log = xes_importer.apply("compressed_input_data/01_running-example.xes.gz")
        from pm4py.algo.discovery.inductive import algorithm as inductive_miner
        tree = inductive_miner.apply(log)
        from pm4py.algo.conformance.alignments.process_tree.variants import milp
        al = milp.apply(log, tree)

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


    def test_alignments_variant_return_value(self):
        import pm4py
        log = pm4py.read_xes("input_data/roadtraffic100traces.xes")
        net, im, fm = pm4py.discover_petri_net_inductive(log)
        alignments = align_alg.apply(log, net, im, fm, variant=align_alg.Variants.VERSION_STATE_EQUATION_A_STAR,
                                     parameters={align_alg.Parameters.UNPACK_VARIANT_ALIGNMENTS: False})

        self.assertEqual(len(alignments), 10)
        self.assertEqual(sum(map(lambda a: a[1], alignments)), 100)

    def test_multiprocessing_timestamp_keys_and_result_formats(self):
        import pm4py

        net, im, fm = process_tree_converter.apply(ProcessTree(label="A"))
        for timestamp_key in ("time:timestamp", "custom_timestamp"):
            log = EventLog([
                Trace([
                    Event({
                        "concept:name": activity,
                        timestamp_key: datetime(2024, 1, 1, tzinfo=timezone.utc)
                        + timedelta(seconds=position),
                    })
                    for position, activity in enumerate(activities)
                ], attributes={"concept:name": str(case_id)})
                for case_id, activities in enumerate((("A",), ("A", "B"), ("A",)))
            ])
            dataframe = pm4py.convert_to_dataframe(log)
            for obj in (log, dataframe):
                for unpack_alignments in (True, False):
                    with self.subTest(
                        timestamp_key=timestamp_key,
                        log_type=type(obj).__name__,
                        unpack_alignments=unpack_alignments,
                    ):
                        parameters = {
                            align_alg.Parameters.CORES: 1,
                            align_alg.Parameters.SHOW_PROGRESS_BAR: False,
                            align_alg.Parameters.UNPACK_VARIANT_ALIGNMENTS: unpack_alignments,
                        }
                        if timestamp_key != "time:timestamp":
                            parameters[align_alg.Parameters.TIMESTAMP_KEY] = timestamp_key
                        results = align_alg.apply_multiprocessing(
                            obj, net, im, fm,
                            variant=align_alg.Variants.VERSION_DIJKSTRA_LESS_MEMORY,
                            parameters=parameters,
                        )
                        if not unpack_alignments:
                            if obj is dataframe:
                                self.assertEqual([2, 1], [count for _, count in results])
                            results = [alignment for alignment, _ in results]
                        expected_costs = [0, 10000, 0] if unpack_alignments else [0, 10000]
                        self.assertEqual(expected_costs, [result["cost"] for result in results])
                        self.assertEqual([("A", "A")], results[0]["alignment"])
                        self.assertEqual([("A", "A"), ("B", ">>")], results[1]["alignment"])


if __name__ == "__main__":
    unittest.main()

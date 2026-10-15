import json
import logging
import os, sys
import subprocess
import textwrap
import unittest
from collections import Counter
from itertools import permutations
from unittest.mock import patch

from pm4py.objects.conversion.log import converter as log_conversion
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
from pm4py.algo.conformance.tokenreplay.variants.token_replay import NoConceptNameException
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.objects import petri_net
from pm4py.objects.log.util import dataframe_utils
from pm4py.util import constants, pandas_utils
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.util import sampling, sorting, index_attribute
from pm4py.objects.petri_net.exporter import exporter as petri_exporter
from pm4py.visualization.petri_net.common import visualize as pn_viz
from pm4py.objects.conversion.process_tree import converter as process_tree_converter

# from tests.constants import INPUT_DATA_DIR, OUTPUT_DATA_DIR, PROBLEMATIC_XES_DIR

INPUT_DATA_DIR = "input_data"
OUTPUT_DATA_DIR = "test_output_data"
PROBLEMATIC_XES_DIR = "xes_importer_tests"
COMPRESSED_INPUT_DATA = "compressed_input_data"


class InductiveMinerTest(unittest.TestCase):
    def test_xor_projection_ties_are_independent_of_component_order(self):
        from pm4py.algo.discovery.inductive.cuts.xor import ExclusiveChoiceCutUVCL
        from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL
        from pm4py.objects.dfg.obj import DFG

        # Noise filtering can disconnect activities that still share a trace.
        variants = Counter({
            ("a", "b"): 3,
            ("c", "d"): 2,
            ("a", "c", "b", "d"): 7,
            ("a", "a", "c"): 5,
            ("z",): 4,
        })
        dfg = DFG(
            {("a", "b"): 3, ("c", "d"): 2},
            {"a": 3, "c": 2, "z": 4},
            {"b": 3, "d": 2, "z": 4},
        )
        obj = IMDataStructureUVCL(variants, dfg)
        expected = {
            frozenset({"a", "b"}): Counter({("a", "b"): 3, ("a", "a"): 5}),
            frozenset({"c", "d"}): Counter({("c", "d"): 9}),
            frozenset({"z"}): Counter({("z",): 4}),
        }

        for components in permutations([{"a", "b"}, {"c", "d"}, {"z"}]):
            with self.subTest(components=components):
                with patch(
                    "pm4py.algo.discovery.inductive.cuts.xor.nx_utils.connected_components",
                    return_value=components,
                ):
                    groups = ExclusiveChoiceCutUVCL.holds(obj)
                projected = ExclusiveChoiceCutUVCL.project(obj, groups)
                self.assertEqual(expected, {
                    frozenset(group): sublog.data_structure
                    for group, sublog in zip(groups, projected)
                })

    def test_receipt_imf_is_independent_of_hash_seed(self):
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        receipt_path = os.path.join(repo_root, "tests", "input_data", "receipt.xes")
        script = textwrap.dedent("""\
            import json
            import sys
            import pm4py

            log = pm4py.read_xes(sys.argv[1], show_progress_bar=False)
            results = []
            for threshold, disabled in [(0.0, False), (0.2, False), (0.2, True)]:
                parameters = dict(noise_threshold=threshold, disable_fallthroughs=disabled)
                tree = pm4py.discover_process_tree_inductive(log, **parameters)
                net, _, _ = pm4py.discover_petri_net_inductive(log, **parameters)
                results.append({
                    "tree": str(tree),
                    "transitions": len(net.transitions),
                    "labels": sorted(t.label for t in net.transitions if t.label is not None),
                })
            print(json.dumps(results))
        """)
        models = []
        for seed in (0, 5):
            result = subprocess.run(
                [sys.executable, "-c", script, receipt_path],
                cwd=repo_root,
                env={**os.environ, "PYTHONHASHSEED": str(seed)},
                capture_output=True,
                text=True,
                check=True,
                timeout=60,
            )
            models.append(json.loads(result.stdout))

        self.assertEqual(models[0], models[1])
        self.assertEqual([74, 69, 38], [model["transitions"] for model in models[0]])
        for model in models[0]:
            for label in (
                "T11 Create document X request unlicensed",
                "T12 Check document X request unlicensed",
                "T13 Adjust document X request unlicensed",
                "T14 Determine document X request unlicensed",
            ):
                self.assertIn(label, model["labels"])

    def obtain_petri_net_through_im(self, log_name, variant=inductive_miner.Variants.IM):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        if ".xes" in log_name:
            log = xes_importer.apply(log_name)
        else:
            df = pandas_utils.read_csv(log_name)
            df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
            log = log_conversion.apply(df, variant=log_conversion.Variants.TO_EVENT_LOG)
        process_tree = inductive_miner.apply(log)
        net, marking, final_marking = process_tree_converter.apply(process_tree)

        return log, net, marking, final_marking

    def test_applyImdfToXES(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        # calculate and compare Petri nets obtained on the same log to verify that instances
        # are working correctly
        log1, net1, marking1, fmarking1 = self.obtain_petri_net_through_im(
            os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        log2, net2, marking2, fmarking2 = self.obtain_petri_net_through_im(
            os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        log1 = sorting.sort_timestamp(log1)
        log1 = sampling.sample(log1)
        log1 = index_attribute.insert_trace_index_as_event_attribute(log1)
        log2 = sorting.sort_timestamp(log2)
        log2 = sampling.sample(log2)
        log2 = index_attribute.insert_trace_index_as_event_attribute(log2)
        petri_exporter.apply(net1, marking1, os.path.join(OUTPUT_DATA_DIR, "running-example.pnml"))
        os.remove(os.path.join(OUTPUT_DATA_DIR, "running-example.pnml"))
        self.assertEqual(len(net1.places), len(net2.places))
        final_marking = petri_net.obj.Marking()
        for p in net1.places:
            if not p.out_arcs:
                final_marking[p] = 1
        aligned_traces = token_replay.apply(log1, net1, marking1, final_marking)
        del aligned_traces

    def test_applyImdfToCSV(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        # calculate and compare Petri nets obtained on the same log to verify that instances
        # are working correctly
        log1, net1, marking1, fmarking1 = self.obtain_petri_net_through_im(
            os.path.join(INPUT_DATA_DIR, "running-example.csv"))
        log2, net2, marking2, fmarking2 = self.obtain_petri_net_through_im(
            os.path.join(INPUT_DATA_DIR, "running-example.csv"))
        log1 = sorting.sort_timestamp(log1)
        log1 = sampling.sample(log1)
        log1 = index_attribute.insert_trace_index_as_event_attribute(log1)
        log2 = sorting.sort_timestamp(log2)
        log2 = sampling.sample(log2)
        log2 = index_attribute.insert_trace_index_as_event_attribute(log2)
        petri_exporter.apply(net1, marking1, os.path.join(OUTPUT_DATA_DIR, "running-example.pnml"))
        os.remove(os.path.join(OUTPUT_DATA_DIR, "running-example.pnml"))
        self.assertEqual(len(net1.places), len(net2.places))
        final_marking = petri_net.obj.Marking()
        for p in net1.places:
            if not p.out_arcs:
                final_marking[p] = 1
        aligned_traces = token_replay.apply(log1, net1, marking1, final_marking)
        del aligned_traces

    def test_imdfVisualizationFromXES(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log, net, marking, fmarking = self.obtain_petri_net_through_im(
            os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        log = sorting.sort_timestamp(log)
        log = sampling.sample(log)
        log = index_attribute.insert_trace_index_as_event_attribute(log)
        petri_exporter.apply(net, marking, os.path.join(OUTPUT_DATA_DIR, "running-example.pnml"))
        os.remove(os.path.join(OUTPUT_DATA_DIR, "running-example.pnml"))
        gviz = pn_viz.graphviz_visualization(net)
        final_marking = petri_net.obj.Marking()
        for p in net.places:
            if not p.out_arcs:
                final_marking[p] = 1
        aligned_traces = token_replay.apply(log, net, marking, final_marking)
        del gviz
        del aligned_traces

    def test_inductive_miner_new_log(self):
        import pm4py
        log = pm4py.read_xes("input_data/running-example.xes", return_legacy_log_object=True)
        tree = pm4py.discover_process_tree_inductive(log, noise_threshold=0.2)

    def test_inductive_miner_new_df(self):
        import pm4py
        log = pm4py.read_xes("input_data/running-example.xes")
        tree = pm4py.discover_process_tree_inductive(log, noise_threshold=0.2)

    def test_inductive_miner_new_log_dfg(self):
        import pm4py
        from pm4py.objects.dfg.obj import DFG
        log = pm4py.read_xes("input_data/running-example.xes", return_legacy_log_object=True)
        dfg, sa, ea = pm4py.discover_dfg(log)
        typed_dfg = DFG(dfg, sa, ea)
        tree = pm4py.discover_process_tree_inductive(typed_dfg, noise_threshold=0.2)

    def test_inductive_miner_new_df_dfg(self):
        import pm4py
        log = pm4py.read_xes("input_data/running-example.xes", return_legacy_log_object=False)
        typed_dfg = pm4py.discover_dfg_typed(log)
        tree = pm4py.discover_process_tree_inductive(typed_dfg, noise_threshold=0.2)

    def test_inductive_miner_new_log_variants(self):
        import pm4py
        from pm4py.util.compression.dtypes import UVCL
        from pm4py.algo.discovery.inductive.variants.imf import IMFUVCL
        from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL
        log = pm4py.read_xes("input_data/running-example.xes", return_legacy_log_object=True)
        variants = pm4py.get_variants(log)
        uvcl = UVCL()
        for var, occ in variants.items():
            uvcl[var] = len(occ)
        parameters = {"noise_threshold": 0.2}
        imfuvcl = IMFUVCL(parameters)

        tree = imfuvcl.apply(IMDataStructureUVCL(uvcl), parameters=parameters)


    def test_inductive_miner_new_df_variants(self):
        import pm4py
        from pm4py.util.compression.dtypes import UVCL
        from pm4py.algo.discovery.inductive.variants.imf import IMFUVCL
        from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL
        log = pm4py.read_xes("input_data/running-example.xes", return_legacy_log_object=True)
        variants = pm4py.get_variants(log)
        uvcl = UVCL()
        for var, occ in variants.items():
            uvcl[var] = len(occ)
        parameters = {"noise_threshold": 0.2}
        imfuvcl = IMFUVCL(parameters)

        tree = imfuvcl.apply(IMDataStructureUVCL(uvcl), parameters=parameters)



if __name__ == "__main__":
    unittest.main()

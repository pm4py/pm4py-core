import logging
import os, sys
import unittest

from pm4py.objects.conversion.log import converter as log_conversion
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
from pm4py.algo.conformance.tokenreplay.variants.token_replay import NoConceptNameException
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.objects import petri_net
import pandas as pd
from pm4py.objects.log.util import dataframe_utils
from pm4py.util import constants
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
    def obtain_petri_net_through_im(self, log_name, variant=inductive_miner.Variants.IM):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        if ".xes" in log_name:
            log = xes_importer.apply(log_name)
        else:
            df = pd.read_csv(log_name)
            df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format="ISO8601")
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

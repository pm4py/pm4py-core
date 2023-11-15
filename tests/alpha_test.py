import logging
import os
import unittest

from pm4py.objects.conversion.log import converter as log_conversion
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
from pm4py.algo.conformance.tokenreplay.variants.token_replay import NoConceptNameException
from pm4py.algo.discovery.alpha import algorithm as alpha_alg
from pm4py.objects import petri_net
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.util import sampling, sorting, index_attribute
from pm4py.objects.petri_net.exporter import exporter as petri_exporter
from pm4py.visualization.petri_net.common import visualize as pn_viz
from pm4py.util import constants
import pandas as pd
from pm4py.objects.log.util import dataframe_utils
from tests.constants import INPUT_DATA_DIR, OUTPUT_DATA_DIR, PROBLEMATIC_XES_DIR


class AlphaMinerTest(unittest.TestCase):
    def obtainPetriNetThroughAlphaMiner(self, log_name):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"

        if ".xes" in log_name:
            log = xes_importer.apply(log_name)
        else:
            df = pd.read_csv(log_name)
            df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format="ISO8601")
            log = log_conversion.apply(df, variant=log_conversion.Variants.TO_EVENT_LOG)
        net, marking, fmarking = alpha_alg.apply(log)

        return log, net, marking, fmarking

    def test_applyAlphaMinerToXES(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        # calculate and compare Petri nets obtained on the same log to verify that instances
        # are working correctly
        log1, net1, marking1, fmarking1 = self.obtainPetriNetThroughAlphaMiner(
            os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        log2, net2, marking2, fmarking2 = self.obtainPetriNetThroughAlphaMiner(
            os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        log1 = sorting.sort_timestamp(log1)
        log1 = sampling.sample(log1)
        log1 = index_attribute.insert_trace_index_as_event_attribute(log1)
        log2 = sorting.sort_timestamp(log2)
        log2 = sampling.sample(log2)
        log2 = index_attribute.insert_trace_index_as_event_attribute(log2)
        self.assertEqual(log2, log2)
        petri_exporter.apply(net1, marking1, os.path.join(OUTPUT_DATA_DIR, "running-example.pnml"))
        os.remove(os.path.join(OUTPUT_DATA_DIR, "running-example.pnml"))
        self.assertEqual(len(net1.places), len(net2.places))
        self.assertEqual(len(net1.transitions), len(net2.transitions))
        self.assertEqual(len(net1.arcs), len(net2.arcs))
        final_marking = petri_net.obj.Marking()
        for p in net1.places:
            if not p.out_arcs:
                final_marking[p] = 1
        aligned_traces = token_replay.apply(log1, net1, marking1, final_marking)
        self.assertEqual(aligned_traces, aligned_traces)

    def test_applyAlphaMinerToCSV(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        # calculate and compare Petri nets obtained on the same log to verify that instances
        # are working correctly
        log1, net1, marking1, fmarking1 = self.obtainPetriNetThroughAlphaMiner(
            os.path.join(INPUT_DATA_DIR, "running-example.csv"))
        log2, net2, marking2, fmarking2 = self.obtainPetriNetThroughAlphaMiner(
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
        self.assertEqual(len(net1.transitions), len(net2.transitions))
        self.assertEqual(len(net1.arcs), len(net2.arcs))
        final_marking = petri_net.obj.Marking()
        for p in net1.places:
            if not p.out_arcs:
                final_marking[p] = 1
        aligned_traces = token_replay.apply(log1, net1, marking1, final_marking)
        self.assertEqual(aligned_traces, aligned_traces)

    def test_alphaMinerVisualizationFromXES(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log, net, marking, fmarking = self.obtainPetriNetThroughAlphaMiner(
            os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        log = sorting.sort_timestamp(log)
        log = sampling.sample(log)
        log = index_attribute.insert_trace_index_as_event_attribute(log)
        petri_exporter.apply(net, marking, os.path.join(OUTPUT_DATA_DIR, "running-example.pnml"))
        os.remove(os.path.join(OUTPUT_DATA_DIR, "running-example.pnml"))
        gviz = pn_viz.graphviz_visualization(net)
        self.assertEqual(gviz, gviz)
        final_marking = petri_net.obj.Marking()
        for p in net.places:
            if not p.out_arcs:
                final_marking[p] = 1
        aligned_traces = token_replay.apply(log, net, marking, fmarking)
        self.assertEqual(aligned_traces, aligned_traces)


if __name__ == "__main__":
    unittest.main()

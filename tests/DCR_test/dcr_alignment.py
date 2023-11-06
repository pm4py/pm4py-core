import os
import unittest
import pandas as pd

import pm4py
from pm4py.algo.conformance.alignments.dcr.variants.optimal import Alignment, Performance, TraceAlignment
from pm4py.algo.discovery.dcr_discover.algorithm import apply
from pm4py.objects.conversion.log import converter as log_converter


class TestAlignment(unittest.TestCase):

    def setUp(self):
        log_path = os.path.join("../input_data", "running-example.xes")
        self.log = pm4py.read_xes(log_path)
        if isinstance(self.log, pd.DataFrame):
            self.log = log_converter.apply(self.log)
        self.dcr_result = apply(self.log, pm4py.algo.discovery.dcr_discover.variants.dcr_discover)
        self.dcr_graph = self.dcr_result[0]
        self.assertIsNotNone(self.dcr_graph)
        self.first_trace = self.log[0]

    def test_initial_alignment(self):
        graph_handler = self.create_graph_handler(self.dcr_graph)
        trace_handler = self.create_trace_handler(self.first_trace)

        alignment_obj = Alignment(graph_handler, trace_handler)
        aligned_traces = alignment_obj.apply_trace()

        self.validate_alignment(aligned_traces)

    def test_trace_alignments(self):
        for trace in self.log:
            self.check_trace_alignment(trace)

    def test_alignment_costs(self):
        graph_handler = self.create_graph_handler(self.dcr_graph)
        trace_handler = self.create_trace_handler(self.first_trace)

        alignment_obj = Alignment(graph_handler, trace_handler)
        aligned_traces = alignment_obj.apply_trace()
        self.check_alignment_cost(aligned_traces)

    def test_final_alignment(self):
        trace_alignment = TraceAlignment(self.dcr_graph, self.first_trace)
        alignment_result = trace_alignment.perform_alignment()
        performance_metrics = trace_alignment.get_performance_metrics()

        self.assertIsNotNone(alignment_result)
        self.assertIsNotNone(performance_metrics)

        print(f"Alignment Result: {alignment_result}")
        print(f"Performance Metrics: {performance_metrics}")

    @staticmethod
    def create_graph_handler(dcr_graph):
        return pm4py.algo.conformance.alignments.dcr.variants.optimal.DCRGraphHandler(dcr_graph)

    @staticmethod
    def create_trace_handler(trace):
        return pm4py.algo.conformance.alignments.dcr.variants.optimal.TraceHandler(trace, 'concept:name')

    def validate_alignment(self, aligned_traces):
        self.assertIsNotNone(aligned_traces)
        self.assertIsInstance(aligned_traces, dict)
        self.assertIn('alignment', aligned_traces)

    def check_trace_alignment(self, trace):
        graph_handler = self.create_graph_handler(self.dcr_graph)
        trace_handler = self.create_trace_handler(trace)

        alignment_obj = Alignment(graph_handler, trace_handler)
        dcr_trace_result = alignment_obj.apply_trace()

        self.assertIsNotNone(dcr_trace_result)
        self.assertIn('alignment', dcr_trace_result)
        self.assertGreaterEqual(len(trace), len(dcr_trace_result['alignment']))

        if len(trace) > 0:
            self.assertNotEqual(len(dcr_trace_result['alignment']), 0)

    def check_alignment_cost(self, aligned_traces):
        alignment = aligned_traces['alignment']
        alignment_cost = aligned_traces.get('cost', float('inf'))
        self.assertEqual(alignment_cost, aligned_traces.get('global_min', float('inf')))

        model_moves = sum(1 for move in alignment if move[0] == 'model')
        log_moves = sum(1 for move in alignment if move[0] == 'log')
        expected_cost = model_moves + log_moves
        self.assertEqual(expected_cost, alignment_cost)


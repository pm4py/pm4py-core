import os
import unittest
import pandas as pd

import pm4py
from pm4py.algo.conformance.alignments.dcr.variants.optimal import Alignment
from pm4py.algo.discovery.dcr_discover.algorithm import apply
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.dcr.importer.variants.xml_dcr_portal import apply as imp_apply


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

    def test_Check_model_moves(self):
        #remove event from log
        trace = [e["concept:name"] for e in self.first_trace]
        trace.remove("check ticket")
        graph_handler = self.create_graph_handler(self.dcr_graph)
        trace_handler = self.create_trace_handler(trace)
        alignment_obj = Alignment(graph_handler, trace_handler)
        aligned_traces = alignment_obj.apply_trace()
        self.check_alignment_cost(aligned_traces)
        self.check_trace_alignment(trace)

    def test_Check_log_moves(self):
        #remove event from log
        trace = [e["concept:name"] for e in self.first_trace]
        trace.append("check ticket")
        graph_handler = self.create_graph_handler(self.dcr_graph)
        trace_handler = self.create_trace_handler(trace)
        alignment_obj = Alignment(graph_handler, trace_handler)
        aligned_traces = alignment_obj.apply_trace()
        self.check_alignment_cost(aligned_traces)
        self.check_trace_alignment(trace)

    def test_combination(self):
        #remove event from log
        trace = [e["concept:name"] for e in self.first_trace]
        trace[3] = "reject request"
        trace.insert(5,"register request")
        trace.pop(8)
        graph_handler = self.create_graph_handler(self.dcr_graph)
        trace_handler = self.create_trace_handler(trace)
        alignment_obj = Alignment(graph_handler, trace_handler)
        aligned_traces = alignment_obj.apply_trace()
        print(aligned_traces)
        self.check_alignment_cost(aligned_traces)
        self.check_trace_alignment(trace)

    def test_log_simple_interface(self):
        log_path = os.path.join("../input_data", "running-example.xes")
        self.log = pm4py.read_xes(log_path)
        res = pm4py.optimal_alignment_dcr(self.log,self.dcr_graph)
        for i in res:
            self.assertTrue(i['move_model_fitness'] == 1.0)
            self.assertTrue(i['move_log_fitness'] == 1.0)

    def test_fitness(self):
        res = pm4py.optimal_alignment_dcr(self.first_trace,self.dcr_graph)
        self.assertTrue(res['move_model_fitness'] == 1.0)
        self.assertTrue(res['move_log_fitness'] == 1.0)

    def test_return_datafrane(self):
        log_path = os.path.join("../input_data", "running-example.xes")
        self.log = pm4py.read_xes(log_path)
        res = pm4py.optimal_alignment_dcr(self.log, self.dcr_graph,return_diagnostics_dataframe=True)
        self.assertIsInstance(res,pd.DataFrame)
        for index,row in res.iterrows():
            self.assertTrue(row['move_model_fitness'] == 1.0)
            self.assertTrue(row['move_log_fitness'] == 1.0)

    def test_imported_dcr(self):
        # test to see if the optimal alignment can run imported dcr
        from pm4py.objects.dcr.importer.variants.xml_dcr_portal import apply as importer
        dcr = importer("../input_data/DCR_test_Claims/DCR_test_Claims.xml")
        log = pm4py.read_xes("../input_data/DCR_test_Claims/event_log.xes")
        log = log[log["lifecycle:transition"] != "complete"]
        res = pm4py.optimal_alignment_dcr(log,dcr)

    @staticmethod
    def create_graph_handler(dcr_graph):
        return pm4py.algo.conformance.alignments.dcr.variants.optimal.DCRGraphHandler(dcr_graph)

    @staticmethod
    def create_trace_handler(trace):
        return pm4py.algo.conformance.alignments.dcr.variants.optimal.TraceHandler(trace, 'concept:name')

    @staticmethod
    def create_log_handler(log):
        return pm4py.algo.conformance.alignments.dcr.variants.optimal.LogAlignment(log, 'concept:name')

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
        self.assertGreaterEqual(len(dcr_trace_result['alignment']),len(trace))

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

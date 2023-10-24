import os
import unittest
import pandas as pd
import time

import pm4py
from pm4py.algo.discovery.dcr_discover.algorithm import apply
from pm4py.objects.conversion.log import converter as log_converter


class TestDcr(unittest.TestCase):
    def test_align_dcr_log_new_version(self):
        log = pm4py.read_xes(os.path.join("../input_data", "running-example.xes"))
        if isinstance(log, pd.DataFrame):
            log = log_converter.apply(log)
        from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
        from pm4py.algo.conformance.alignments.dcr.variants import optitest

        dcr_result = apply(log, dcr_discover)
        dcr_graph = dcr_result[0]

        # Assertions to check the graph
        self.assertIsNotNone(dcr_graph)

        first_trace = log[0]
        graph_handler = optitest.DCRGraphHandler(dcr_graph)
        trace_handler = optitest.TraceHandler(first_trace, 'concept:name')

        start_time = time.time()
        alignment_obj = optitest.Alignment(graph_handler, trace_handler)
        aligned_traces = alignment_obj.apply_trace()
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"################## Time taken for alignment: {elapsed_time} seconds")

        print(f"aligned traces: {aligned_traces}")

        # Assertions to check the alignment
        self.assertIsNotNone(aligned_traces)
        self.assertIsInstance(aligned_traces, dict)
        self.assertIn('alignment', aligned_traces)

        alignment = aligned_traces['alignment']
        self.assertIsNotNone(alignment)

        # Validate length of alignment
        if isinstance(first_trace, dict) and 'events' in first_trace:
            num_events = len(first_trace['events'])
        else:
            num_events = len(first_trace)
        self.assertEqual(len(alignment), num_events)

        # Loop through all traces in the log
        for trace in log:
            graph_handler = optitest.DCRGraphHandler(dcr_graph)
            trace_handler = optitest.TraceHandler(trace, 'concept:name')
            alignment_obj = optitest.Alignment(graph_handler, trace_handler)
            dcr_trace_result = alignment_obj.apply_trace()

            self.assertIsNotNone(dcr_trace_result)
            self.assertIn('alignment', dcr_trace_result)
            self.assertGreaterEqual(len(dcr_trace_result['alignment']), len(trace))
            if len(trace) > 0:
                self.assertNotEqual(len(dcr_trace_result['alignment']), 0)

        # Cost Checks
        alignment_cost = aligned_traces.get('cost', float('inf'))
        self.assertEqual(alignment_cost, aligned_traces.get('global_min', float('inf')))

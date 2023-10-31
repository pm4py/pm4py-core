import os
import unittest
import pandas as pd
import time
from copy import deepcopy

import pm4py
from pm4py.algo.discovery.dcr_discover.algorithm import apply
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.algo.conformance.alignments.dcr import algorithm as dcr_alignment
from pm4py.objects.log.obj import Trace

from pm4py.objects.dcr.importer import importer as dcr_importer
from pm4py.objects.dcr.exporter import exporter as dcr_exporter
from pm4py.objects.conversion.dcr import *

class TestDcr(unittest.TestCase):

    #TODO: create a dict DCR graph and the same graph in the portal
    # it has to have: all relations + self relations + time

    def test_importer_from_portal(self):
        pass

    def test_exporter_to_xml_simple(self):
        pass

    def test_execution_semantics(self):
        pass

    def write_more_tests(self):
        pass

    def test_Basic_DisCoveR_new_DCR_structure(self):
        from pm4py.objects.dcr.obj import DCR_Graph
        #given an event log
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
        #when mined
        dcr, la = apply(log, dcr_discover, findAdditionalConditions=False)

        #then we will get a process model with the same amount of events, hopefully with conditions, response, includes and excludes relations
        self.assertEqual(len(log.index),len(dcr.events))
        self.assertEqual(set(log['concept:name'].unique()),dcr.labels)
        self.assertEqual(len(dcr.labelMapping),len(log.index))
        self.assertEqual(set(dcr.labelMapping.values()), set(log['concept:name'].unique()))
        self.assertIsNotNone(dcr.conditionsFor)
        self.assertIsNotNone(dcr.responseTo)
        self.assertIsNotNone(dcr.includesTo)
        self.assertIsNotNone(dcr.excludesTo)

        # every activity included, and pending and executed being empty
        self.assertEqual(len(dcr.marking.pending), 0)
        self.assertEqual(len(dcr.marking.executed), 0)
        self.assertEqual(len(dcr.marking.included), len(dcr.labels))


    def test_Basic_DisCover_with_AdditionalConditions(self):
        log = pm4py.read_xes(os.path.join("input_data/pdc", "pdc_2020_0011011.xes"))
        from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
        dcr, la = apply(log, dcr_discover)
        print(dcr)
        # then we will get a process model with the same amount of events, hopefully with conditions, response, includes and excludes relations
        self.assertEqual(len(log.index), len(dcr.events))
        self.assertEqual(set(log['concept:name'].unique()), dcr.labels)
        self.assertEqual(len(dcr.labelMapping), len(log.index))
        self.assertEqual(set(dcr.labelMapping.values()), set(log['concept:name'].unique()))
        self.assertIsNotNone(dcr.conditionsFor)
        self.assertIsNotNone(dcr.responseTo)
        self.assertIsNotNone(dcr.includesTo)
        self.assertIsNotNone(dcr.excludesTo)

        # every activity included, and pending and executed being empty
        self.assertEqual(len(dcr.marking.pending), 0)
        self.assertEqual(len(dcr.marking.executed), 0)
        self.assertEqual(len(dcr.marking.included), len(dcr.labels))


    def test_basic_discover_reviewing(self):
        #testing for bigger event logs, to see coherence, and no failure happens with bigger amounts
        log = pm4py.read_xes(os.path.join("input_data", "reviewing.xes"))
        from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
        dcr, la = apply(log, dcr_discover)
        # then we will get a process model with the same amount of events, hopefully with conditions, response, includes and excludes relations
        self.assertEqual(len(log.index), len(dcr.events))
        self.assertEqual(set(log['concept:name'].unique()), dcr.labels)
        self.assertEqual(len(dcr.labelMapping), len(log.index))
        self.assertEqual(set(dcr.labelMapping.values()), set(log['concept:name'].unique()))
        self.assertIsNotNone(dcr.conditionsFor)
        self.assertIsNotNone(dcr.responseTo)
        self.assertIsNotNone(dcr.includesTo)
        self.assertIsNotNone(dcr.excludesTo)

        # every activity included, and pending and executed being empty
        self.assertEqual(len(dcr.marking.pending), 0)
        self.assertEqual(len(dcr.marking.executed), 0)
        self.assertEqual(len(dcr.marking.included), len(dcr.labels))

    def test_DCR_semantics_enabled(self):
        #given an eventlog
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
        dcr, la = apply(log, dcr_discover)
        #when an event is check for being enabled
        from pm4py.objects.dcr.semantics import DCRSemantics
        sem = DCRSemantics()
        #Then register request should return true, and other events not meet the conditions relation is not
        self.assertTrue(sem.is_enabled(log.iloc[0]["concept:name"], dcr))
        self.assertFalse(sem.is_enabled(log.iloc[1]["concept:name"], dcr))

    def test_DCR_execution_semantic(self):
        #given a graph from the DisCover miner
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
        dcr, la = apply(log, dcr_discover)
        # When event is executed, the event that has the event as a condition can then be executed
        from pm4py.objects.dcr.semantics import DCRSemantics
        sem = DCRSemantics()
        if sem.is_enabled(log.iloc[0]["concept:name"], dcr):
            dcr = sem.execute(dcr, log.iloc[0]["concept:name"])

        self.assertTrue(sem.is_enabled(log.iloc[1]["concept:name"], dcr))

    def test_DCR_is_accepting_semantic(self):
        #given a DCR graph discovered from Discover, is always initially accepting
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
        dcr, la = apply(log, dcr_discover)
        log = pm4py.convert_to_event_log(log)
        #this is not relevant to this test, but shows, how the event log object works
        # the abstraction log might be needed for later implementation, but the base implementation
        for traces in log:
            for e in traces:
                print(e['Activity'])
            break
        #then the DCR is accepting
        from pm4py.objects.dcr.semantics import DCRSemantics
        sem = DCRSemantics()
        self.assertTrue(sem.is_accepting(dcr))

    def test_align_dcr_log(self):
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))

        # If log is a DataFrame, convert it to an EventLog
        if isinstance(log, pd.DataFrame):
            log = log_converter.apply(log)

        from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
        from pm4py.algo.conformance.alignments.dcr.variants import optimal

        dcr_result = apply(log, dcr_discover)
        dcr_graph = dcr_result[0]
        print(f"Debug: Type of dcr_graph: {type(dcr_graph)}")
        print(f"Debug: Initial state of DCR graph: {dcr_graph}")

        first_trace = log[0]

        # Test for the first trace
        try:
            aligned_traces = optimal.apply_trace(first_trace, dcr_graph)
        except Exception as e:
            self.fail(f"An error occurred: {e}")

        alignment = aligned_traces.get('alignment', None) if aligned_traces else None
        self.assertIsNotNone(aligned_traces)
        self.assertIsNotNone(alignment)

        self.assertEqual(len(first_trace), len(alignment))
        for event, align_tuple in zip(first_trace, alignment):
            self.assertEqual(event['concept:name'], align_tuple[2]['concept:name'])

        print("First trace passed all assertions.")

        cost = aligned_traces.get('cost', None)
        self.assertEqual(cost, 0)

        print("First trace cost is zero.")

        print("Testing alignment on all traces in the log...")

        # Test for all traces in the log
        for trace in log:
            try:
                dcr_trace_result = optimal.apply(trace, dcr_graph)
            except Exception as e:
                self.fail(f"An error occurred when aligning trace: {e}")

            alignment = dcr_trace_result.get('alignment', [])
            is_fit = all(event['concept:name'] == align_tuple[2]['concept:name'] for event, align_tuple in zip(trace, alignment))

            if not is_fit:
                raise Exception("should be fit")
            print(f"Trace with events {[event['concept:name'] for event in trace]} is fit.")

    def test_align_dcr_log_new_version(self):
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
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



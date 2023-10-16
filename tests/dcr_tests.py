import os
import unittest
import pandas as pd
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
        print(f"Debug: Content of dcr_graph: {dcr_graph}")

        first_trace = log[0]

        # Test for the first trace
        try:
            aligned_traces = optimal.apply_trace(first_trace, dcr_graph)
        except Exception as e:
            self.fail(f"An error occurred: {e}")

        alignment = aligned_traces.get('alignment', None) if aligned_traces else None
        print("Old version - aligned_traces:", aligned_traces)
        print("Old version - dcr_graph state:", dcr_graph)
        print("Old version - first_trace state:", first_trace)
        self.assertIsNotNone(aligned_traces)
        self.assertIsNotNone(alignment)
        print(f"Content of first_trace: {first_trace}")
        print(f"Content of alignment: {alignment}")
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

    """
    def test_align_dcr_log_new_version(self):
          # import your new version here
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))

        if isinstance(log, pd.DataFrame):
            log = log_converter.apply(log)

        from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
        from pm4py.algo.conformance.alignments.dcr.variants import optitest

        dcr_result = apply(log, dcr_discover)
        dcr_graph = dcr_result[0]
        print(f"Debug: Type of dcr_graph: {type(dcr_graph)}")
        print(f"Debug: Content of dcr_graph: {dcr_graph}")

        first_trace = log[0]

        try:
            graph_handler = optitest.DCRGraphHandler(dcr_graph)
            trace_handler = optitest.TraceHandler(first_trace, 'concept:name')
            cost_function = {}

            alignment_obj = optitest.Alignment(graph_handler, trace_handler, cost_function)



            print(f"Debug: Type of alignment_obj: {type(alignment_obj)}")
            print(f"Debug: Content of alignment_obj: {alignment_obj}")
            print("Debug: About to apply_trace")
            # print(f"Debug: Type of trace_handler.trace: {type(trace_handler.trace)}, Content: {trace_handler.trace}")
            aligned_traces = alignment_obj.apply_trace()
            print("New version - aligned_traces:", aligned_traces)  # or whatever stores the aligned traces
            # print("New version - dcr_graph state:", self.graph_handler.graph)
            # print("New version - first_trace state:", self.trace_handler.trace)
            # Inside test_align_dcr_log_new_version
            print(f"Debug: aligned_traces = {aligned_traces}")

            print("Debug: Successfully applied trace")

            if isinstance(aligned_traces, dict) and 'alignment' in aligned_traces:
                alignment = aligned_traces['alignment']
            else:
                self.fail("aligned_traces is not as expected")


            # if len(alignment) != len(first_trace['events']):
            #     self.fail(
            #         f"Length mismatch: first_trace has {len(first_trace['events'])} events but alignment has {len(alignment)}")


        except Exception as e:
            print(f"Debug: Error occurred, {e}")

            # Debugging: Print the type of graph if available
            # if 'graph' in locals():
            #     print(f"Debug: Type of graph during exception: {type(graph)}")

            self.fail(f"An error occurred: {e}")

        # Perform the same checks as in the original version
        alignment = aligned_traces.get('alignment', None) if aligned_traces else None
        self.assertIsNotNone(aligned_traces)
        self.assertIsNotNone(alignment)
        print("Debug: Type of first_trace:", type(first_trace))
        print("Debug: Content of first_trace:", first_trace)

        if isinstance(first_trace, dict) and 'events' in first_trace:
            print("Debug: Type of first_trace['events']:", type(first_trace['events']))
            print("Debug: Content of first_trace['events']:", first_trace['events'])

        print("Debug: Type of alignment:", type(alignment))
        print("Debug: Content of alignment:", alignment)

        if isinstance(first_trace, dict) and 'events' in first_trace:
            num_events = len(first_trace['events'])
        else:
            self.fail(
                f"first_trace is not a dictionary or doesn't contain an 'events' key. It is of type {type(first_trace)}")
            return

        print(f"Debug: num_events in first_trace: {num_events}")

        if len(alignment) != num_events:
            self.fail(f"Length mismatch: first_trace has {num_events} events but alignment has {len(alignment)}")

        self.assertEqual(len(first_trace), len(alignment))
        for event, align_tuple in zip(first_trace, alignment):


            if isinstance(align_tuple[2], str):
                self.assertEqual(event['concept:name'], align_tuple[2])
            else:
                self.assertEqual(event['concept:name'], align_tuple[2]['concept:name'])

        print("First trace passed all assertions.")

        cost = aligned_traces.get('cost', None)
        self.assertEqual(cost, 0)


        for trace in log:
            try:
                graph_handler = optitest.DCRGraphHandler(dcr_graph)
                trace_handler = optitest.TraceHandler(trace, 'concept:name')
                alignment_obj = optitest.Alignment(graph_handler, trace_handler, cost_function)
                dcr_trace_result = alignment_obj.apply_trace()

            except Exception as e:
                self.fail(f"An error occurred when aligning trace: {e}")

            alignment = dcr_trace_result.get('alignment', [])
            is_fit = all(
                (event['concept:name'] == align_tuple[2] if isinstance(align_tuple[2], str)
                 else event['concept:name'] == align_tuple[2]['concept:name'])
                for event, align_tuple in zip(trace, alignment)
            )
            if not is_fit:
                raise Exception("should be fit")
            print(f"Trace with events {[event['concept:name'] for event in trace]} is fit.")

    """

    def test_align_dcr_log_new_version(self):
        try:
            # Setup
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
            cost_function = {}

            # Create and apply alignment
            alignment_obj = optitest.Alignment(graph_handler, trace_handler, cost_function)
            aligned_traces = alignment_obj.apply_trace()

            # Assertions to check the alignment
            self.assertIsNotNone(aligned_traces)
            self.assertIsInstance(aligned_traces, dict)
            self.assertIn('alignment', aligned_traces)

            alignment = aligned_traces['alignment']
            self.assertIsNotNone(alignment)
            print("#######################")
            print(f"Content of first_trace: {first_trace}")
            print(f"Content of alignment: {alignment}")
            print("#######################")

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
                alignment_obj = optitest.Alignment(graph_handler, trace_handler, cost_function)
                dcr_trace_result = alignment_obj.apply_trace()

                # More assertions can be added here to validate each aligned trace
                self.assertIsNotNone(dcr_trace_result)
                self.assertIn('alignment', dcr_trace_result)

        except Exception as e:
            self.fail(f"An error occurred: {e}")

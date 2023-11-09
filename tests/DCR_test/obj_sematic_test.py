import os
import unittest

import pm4py
from pm4py.algo.discovery.dcr_discover.algorithm import apply
from pm4py.objects.dcr.obj import DcrGraph, dcr_template


class TestObjSematics(unittest.TestCase):
    def test_getitem(self):
        # given an event log
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
        # when a dcr is mine
        dcr, la = apply(log, dcr_discover)
        # then dcr graph should be able to be called as a dictionary
        self.assertEqual(dcr['conditionsFor'], dcr.conditions)

    def test_getitem_inheritance(self):
        # given an event log
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        # when mined
        dcr, la = pm4py.discover_dcr(log, process_type={'roles'}, group_key="org:resource")
        # getitem should be able to call the additional variables associated with the role object
        self.assertEqual(dcr['roles'], dcr.roles)
        self.assertEqual(dcr['principals'], dcr.principals)
        self.assertEqual(dcr['roleAssignments'], dcr.role_assignments)

    def test_dcr_semantics_enabled(self):
        # given an eventlog
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
        dcr, la = apply(log, dcr_discover)
        # when an event is check for being enabled
        from pm4py.objects.dcr.semantics import DCRSemantics
        sem = DCRSemantics()
        # Then register request should return true, and other event has yet met conditions is false
        self.assertTrue(sem.is_enabled(log.iloc[0]["concept:name"], dcr))
        self.assertFalse(sem.is_enabled(log.iloc[1]["concept:name"], dcr))

    def test_dcr_execution_semantic(self):
        # given a graph from the DisCover miner
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
        dcr, la = apply(log, dcr_discover)
        # When event is executed, the event that has the event as a condition can then be executed
        from pm4py.objects.dcr.semantics import DCRSemantics
        sem = DCRSemantics()
        if sem.is_enabled(log.iloc[0]["concept:name"], dcr):
            dcr = sem.execute(dcr, log.iloc[0]["concept:name"])

        self.assertTrue(sem.is_enabled(log.iloc[1]["concept:name"], dcr))

    def test_dcr_is_accepting_semantic(self):
        # given a DCR graph discovered from Discover, is always initially accepting
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
        dcr, la = apply(log, dcr_discover)
        # then the DCR is accepting
        from pm4py.objects.dcr.semantics import DCRSemantics
        sem = DCRSemantics()
        self.assertTrue(sem.is_accepting(dcr))

    def test_dcr_is_accepting_response_pending(self):
        # given a DCR graph discovered from Discover, is always initially accepting
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
        dcr, la = apply(log, dcr_discover)
        # when an event triggers a response relation
        from pm4py.objects.dcr.semantics import DCRSemantics
        sem = DCRSemantics()
        sem.execute(dcr, "register request")
        self.assertFalse(sem.is_accepting(dcr))

    def test_label_mapping_to_activity(self):
        from pm4py.objects.dcr.importer.variants.xml_dcr_portal import apply as import_apply
        # given a dcr graph and event log
        # we use this as it provides an dcr graph, with eventIDs and labels and label mapping
        dcr = import_apply('input_data/DCR_test_Claims/DCR_test_Claims.xml')
        log = pm4py.read_xes('input_data/DCR_test_Claims/event_log.xes')
        # when labels are retried for the label mapping
        result = []
        for i in dcr.events:
            result.append(dcr.get_activity(i))
        # then all the labels retrieve should exist in labels
        for i in result:
            self.assertIsInstance(i, str)
            self.assertIn(i, log['concept:name'].tolist())

    def test_label_Mapping_to_eventID(self):
        from pm4py.objects.dcr.importer.variants.xml_dcr_portal import apply as import_apply
        # given a dcr graph and event log
        # we use this as it provides an dcr graph, with eventIDs and labels and label mapping
        dcr = import_apply('input_data/DCR_test_Claims/DCR_test_Claims.xml')
        log = pm4py.read_xes('input_data/DCR_test_Claims/event_log.xes')
        log = log[log['concept:name'] != 'end']
        # when labels are retried for the label mapping
        result = []
        for _, row in log.iterrows():
            result.append(dcr.get_event(row['concept:name']))
            # then all the labels retrieve should exist in labels
        for i in result:
            self.assertIsInstance(i, str)
            self.assertIn(i, dcr['events'])

    def test_pending_event(self):
        from pm4py.objects.dcr.importer.variants.xml_dcr_portal import apply as import_apply
        # given a dcr graph and event log
        # we use this as it provides an dcr graph, with eventIDs and labels and label mapping
        dcr = import_apply('test_output_data/pendingEvent.xml')
        self.assertEqual(1, len(dcr.marking.pending))

    def test_instantiate_object(self):
        dcr1 = DcrGraph()
        dcr2 = DcrGraph(dcr_template)
        # both empty should be equal
        self.assertEqual(dcr1, dcr2)
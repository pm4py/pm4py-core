import os
import unittest

import pm4py
from pm4py.algo.discovery.dcr_discover.algorithm import apply
from pm4py.algo.discovery.dcr_discover.variants import dcr_discover as disc_alg
from pm4py.objects.dcr.importer import importer as dcr_importer
from pm4py.objects.dcr.importer.variants.xml_dcr_portal import apply as import_apply
from pm4py.objects.dcr.exporter import exporter as dcr_exporter
from pm4py.objects.dcr.exporter.exporter import apply as export_apply
from pm4py.objects.conversion.dcr import *

class TestDcr(unittest.TestCase):

    #TODO: create a dict DCR graph and the same graph in the portal
    # it has to have: all relations + self relations + time

    def test_exporter_to_portal(self):
        event_log_file = os.path.join("input_data", "sepsis", "data", "Sepsis Cases - Event Log.xes")
        dcrxml_file_export = os.path.join("test_output_data", "sepsis_dcr_portal.xml")
        log = pm4py.read_xes(event_log_file)
        dcr, _ = disc_alg.apply(log)
        export_apply(dcr_graph=dcr,path=dcrxml_file_export,variant=dcr_exporter.XML_DCR_PORTAL, dcr_title='xml_2_dcr_portal')

    def test_importer_from_portal(self):
        dcr = import_apply(os.path.join("test_output_data", "sepsis_dcr_portal.xml"))
        self.assertIsNotNone(dcr)

    def test_exporter_to_xml_simple(self):
        event_log_file = os.path.join("input_data", "sepsis", "data", "Sepsis Cases - Event Log.xes")
        dcrxml_file_export = os.path.join("test_output_data", "sepsis_dcr_simple.xml")
        log = pm4py.read_xes(event_log_file)
        dcr, _ = disc_alg.apply(log)
        export_apply(dcr_graph=dcr,path=dcrxml_file_export,variant=dcr_exporter.XML_SIMPLE)

    def test_import_export_portal(self):
        dcr = import_apply(os.path.join("test_output_data", "sepsis_dcr_portal.xml"))
        path = os.path.join("test_output_data", "sepsis_dcr_portal_exported.xml")
        export_apply(dcr_graph=dcr,path=path,variant=dcr_exporter.XML_DCR_PORTAL, dcr_title='sepsis_dcr_portal_exported_xml')
        dcr_imported_after_export = import_apply(path)
        self.assertEqual(len(dcr), len(dcr_imported_after_export))
        os.remove(path)

    # def test_execution_semantics(self):
    #     pass

    # def write_more_tests(self):
    #     pass

    # def test_Basic_DisCoveR_new_DCR_structure(self):
    #     from pm4py.objects.dcr.obj import DCR_Graph
    #     #given an event log
    #     log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
    #     from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
    #     #when mined
    #     dcr, la = apply(log, dcr_discover, findAdditionalConditions=False)

    #     #then we will get a process model with the same amount of events, hopefully with conditions, response, includes and excludes relations
    #     self.assertEqual(len(log.index),len(dcr.events))
    #     self.assertEqual(set(log['concept:name'].unique()),dcr.labels)
    #     self.assertEqual(len(dcr.labelMapping),len(log.index))
    #     self.assertEqual(set(dcr.labelMapping.values()), set(log['concept:name'].unique()))
    #     self.assertIsNotNone(dcr.conditionsFor)
    #     self.assertIsNotNone(dcr.responseTo)
    #     self.assertIsNotNone(dcr.includesTo)
    #     self.assertIsNotNone(dcr.excludesTo)

    #     # every activity included, and pending and executed being empty
    #     self.assertEqual(len(dcr.marking.pending), 0)
    #     self.assertEqual(len(dcr.marking.executed), 0)
    #     self.assertEqual(len(dcr.marking.included), len(dcr.labels))


    # def test_Basic_DisCover_with_AdditionalConditions(self):
    #     log = pm4py.read_xes(os.path.join("input_data/pdc", "pdc_2020_0011011.xes"))
    #     from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
    #     dcr, la = apply(log, dcr_discover)
    #     print(dcr)
    #     # then we will get a process model with the same amount of events, hopefully with conditions, response, includes and excludes relations
    #     self.assertEqual(len(log.index), len(dcr.events))
    #     self.assertEqual(set(log['concept:name'].unique()), dcr.labels)
    #     self.assertEqual(len(dcr.labelMapping), len(log.index))
    #     self.assertEqual(set(dcr.labelMapping.values()), set(log['concept:name'].unique()))
    #     self.assertIsNotNone(dcr.conditionsFor)
    #     self.assertIsNotNone(dcr.responseTo)
    #     self.assertIsNotNone(dcr.includesTo)
    #     self.assertIsNotNone(dcr.excludesTo)

    #     # every activity included, and pending and executed being empty
    #     self.assertEqual(len(dcr.marking.pending), 0)
    #     self.assertEqual(len(dcr.marking.executed), 0)
    #     self.assertEqual(len(dcr.marking.included), len(dcr.labels))


    # def test_basic_discover_reviewing(self):
    #     #testing for bigger event logs, to see coherence, and no failure happens with bigger amounts
    #     log = pm4py.read_xes(os.path.join("input_data", "reviewing.xes"))
    #     from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
    #     dcr, la = apply(log, dcr_discover)
    #     # then we will get a process model with the same amount of events, hopefully with conditions, response, includes and excludes relations
    #     self.assertEqual(len(log.index), len(dcr.events))
    #     self.assertEqual(set(log['concept:name'].unique()), dcr.labels)
    #     self.assertEqual(len(dcr.labelMapping), len(log.index))
    #     self.assertEqual(set(dcr.labelMapping.values()), set(log['concept:name'].unique()))
    #     self.assertIsNotNone(dcr.conditionsFor)
    #     self.assertIsNotNone(dcr.responseTo)
    #     self.assertIsNotNone(dcr.includesTo)
    #     self.assertIsNotNone(dcr.excludesTo)

    #     # every activity included, and pending and executed being empty
    #     self.assertEqual(len(dcr.marking.pending), 0)
    #     self.assertEqual(len(dcr.marking.executed), 0)
    #     self.assertEqual(len(dcr.marking.included), len(dcr.labels))

    # def test_DCR_semantics_enabled(self):
    #     #given an eventlog
    #     log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
    #     from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
    #     dcr, la = apply(log, dcr_discover)
    #     #when an event is check for being enabled
    #     from pm4py.objects.dcr.semantics import DCRSemantics
    #     sem = DCRSemantics()
    #     #Then register request should return true, and other events not meet the conditions relation is not
    #     self.assertTrue(sem.is_enabled(log.iloc[0]["concept:name"], dcr))
    #     self.assertFalse(sem.is_enabled(log.iloc[1]["concept:name"], dcr))

    # def test_DCR_execution_semantic(self):
    #     #given a graph from the DisCover miner
    #     log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
    #     from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
    #     dcr, la = apply(log, dcr_discover)
    #     # When event is executed, the event that has the event as a condition can then be executed
    #     from pm4py.objects.dcr.semantics import DCRSemantics
    #     sem = DCRSemantics()
    #     if sem.is_enabled(log.iloc[0]["concept:name"], dcr):
    #         dcr = sem.execute(dcr, log.iloc[0]["concept:name"])

    #     self.assertTrue(sem.is_enabled(log.iloc[1]["concept:name"], dcr))

    # def test_DCR_is_accepting_semantic(self):
    #     #given a DCR graph discovered from Discover, is always initially accepting
    #     log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
    #     from pm4py.algo.discovery.dcr_discover.variants import dcr_discover
    #     dcr, la = apply(log, dcr_discover)
    #     log = pm4py.convert_to_event_log(log)
    #     #this is not relevant to this test, but shows, how the event log object works
    #     # the abstraction log might be needed for later implementation, but the base implementation
    #     for traces in log:
    #         for e in traces:
    #             print(e['Activity'])
    #         break
    #     #then the DCR is accepting
    #     from pm4py.objects.dcr.semantics import DCRSemantics
    #     sem = DCRSemantics()
    #     self.assertTrue(sem.is_accepting(dcr))

if __name__ == '__main__':
    unittest.main()

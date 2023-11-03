import os
import unittest

import pm4py
from pm4py.algo.discovery.dcr_discover.algorithm import apply, Variants
from pm4py.algo.discovery.dcr_discover.variants import dcr_discover as disc_alg
from pm4py.objects.dcr.importer import importer as dcr_importer
from pm4py.objects.dcr.importer.variants.xml_dcr_portal import apply as import_apply
from pm4py.objects.dcr.exporter import exporter as dcr_exporter
from pm4py.objects.dcr.exporter.exporter import apply as export_apply
from pm4py.objects.conversion.dcr import *

class TestDcr(unittest.TestCase):

    #TODO: create a dict DCR graph and the same graph in the portal
    # it has to have: all relations + self relations + time

    # def test_exporter_to_portal(self):
    #     event_log_file = os.path.join("input_data", "sepsis", "data", "Sepsis Cases - Event Log.xes")
    #     dcrxml_file_export = os.path.join("test_output_data", "sepsis_dcr_portal.xml")
    #     log = pm4py.read_xes(event_log_file)
    #     dcr, _ = disc_alg.apply(log)
    #     export_apply(dcr_graph=dcr,path=dcrxml_file_export,variant=dcr_exporter.XML_DCR_PORTAL, dcr_title='xml_2_dcr_portal')

    # def test_importer_from_portal(self):
    #     dcr = import_apply(os.path.join("test_output_data", "sepsis_dcr_portal.xml"))
    #     self.assertIsNotNone(dcr)

    # def test_exporter_to_xml_simple(self):
    #     event_log_file = os.path.join("input_data", "sepsis", "data", "Sepsis Cases - Event Log.xes")
    #     dcrxml_file_export = os.path.join("test_output_data", "sepsis_dcr_simple.xml")
    #     log = pm4py.read_xes(event_log_file)
    #     dcr, _ = disc_alg.apply(log)
    #     export_apply(dcr_graph=dcr,path=dcrxml_file_export,variant=dcr_exporter.XML_SIMPLE)

    # def test_import_export_portal(self):
    #     dcr = import_apply(os.path.join("test_output_data", "sepsis_dcr_portal.xml"))
    #     path = os.path.join("test_output_data", "sepsis_dcr_portal_exported.xml")
    #     export_apply(dcr_graph=dcr,path=path,variant=dcr_exporter.XML_DCR_PORTAL, dcr_title='sepsis_dcr_portal_exported_xml')
    #     dcr_imported_after_export = import_apply(path)
    #     self.assertEqual(len(dcr), len(dcr_imported_after_export))
    #     os.remove(path)

    # def test_xml_dcr_portal_to_dcr_js_portal(self):
    #     dcr = import_apply(os.path.join("test_output_data", "sepsis_dcr_portal.xml"))
    #     path = os.path.join("test_output_data", "sepsis_dcr_js_portal.xml")
    #     export_apply(dcr_graph=dcr,path=path,variant=dcr_exporter.DCR_JS_PORTAL, dcr_title='sepsis_dcr_js_portal')

    # def test_xes_to_xml_dcr_portal_to_dcr_js_portal(self):
    #     event_log_file = os.path.join("input_data", "running-example.xes")
    #     dcrxml_file_export = os.path.join("test_output_data", "running-example_dcr_portal.xml")
    #     log = pm4py.read_xes(event_log_file)
    #     dcr, _ = disc_alg.apply(log)
    #     export_apply(dcr_graph=dcr,path=dcrxml_file_export,variant=dcr_exporter.XML_DCR_PORTAL, dcr_title='running-example_dcr_portal')
    #     dcr_imported_after_export = import_apply(dcrxml_file_export)
    #     path = os.path.join("test_output_data", "running-example_dcr_js_portal.xml")
    #     export_apply(dcr_graph=dcr_imported_after_export,path=path,variant=dcr_exporter.DCR_JS_PORTAL, dcr_title='running-example_dcr_js_portal')
    #     os.remove(dcrxml_file_export)

    # def test_xes_to_dcr_js_portal(self):
    #     event_log_file = os.path.join("input_data", "receipt.xes")
    #     dcrxml_file_export = "C:/Users/herma/Downloads/receipt_dcr_js_portal.xml"
    #     log = pm4py.read_xes(event_log_file)
    #     dcr, _ = disc_alg.apply(log)
    #     pm4py.write_dcr_xml(dcr_graph=dcr,path=dcrxml_file_export,variant=dcr_exporter.DCR_JS_PORTAL, dcr_title='receipt_dcr_js_portal')

    def test_import_export_portal(self):
        event_log_file = os.path.join("input_data", "receipt.xes")
        dcrxml_file_export = "C:/Users/herma/Downloads/receipt_exported.xml"
        log = pm4py.read_xes(event_log_file)
        # dcr, _ = disc_alg.apply(log)
        dcr, _ = apply(log, variant=Variants.DCR_BASIC)
        # print((dcr['events']))
        pm4py.write_dcr_xml(dcr_graph=dcr, path=dcrxml_file_export, variant=dcr_exporter.Variants.DCR_JS_PORTAL, dcr_title='receipt_exported_dcr_js_portal')

if __name__ == '__main__':
    unittest.main()

import os
import unittest

import pm4py
from pm4py.algo.discovery.dcr_discover import algorithm as disc_alg
from pm4py.objects.dcr.importer import importer as dcr_importer
from pm4py.objects.dcr.exporter import exporter as dcr_exporter

class TestImportExportDCR(unittest.TestCase):

    #TODO: create a dict DCR graph and the same graph in the portal
    # it has to have: all relations + self relations + time

    def test_exporter_to_xml_simple(self):
        event_log_file = os.path.join("../input_data", "receipt.xes")
        dcrxml_file_export = os.path.join("../test_output_data", "receipt_xml_simple.xml")
        log = pm4py.read_xes(event_log_file)
        dcr, _ = disc_alg.apply(log)
        pm4py.write_dcr_xml(dcr_graph=dcr,path=dcrxml_file_export,variant=dcr_exporter.XML_SIMPLE, dcr_title='receipt_xml_simple')

    def test_import_export_xml_simple(self):
        dcr = pm4py.read_dcr_xml(os.path.join("../test_output_data", "receipt_xml_simple.xml"), variant=dcr_importer.Variants.XML_SIMPLE)
        path = os.path.join("../test_output_data", "receipt_xml_simple_exported.xml")
        pm4py.write_dcr_xml(dcr_graph=dcr,path=path,variant=dcr_exporter.Variants.XML_SIMPLE, dcr_title='receipt_xml_simple_exported')
        dcr_imported_after_export = pm4py.read_dcr_xml(path, variant=dcr_importer.Variants.XML_SIMPLE)
        self.assertEqual(len(dcr.__dict__), len(dcr_imported_after_export.__dict__))
        os.remove(path)

    # Events are not included (dashed lines) in the portal
    def test_xml_simple_to_dcr_js_portal(self):
        dcr = pm4py.read_dcr_xml(os.path.join("../test_output_data", "receipt_xml_simple.xml"), variant=dcr_importer.Variants.XML_SIMPLE)
        path = os.path.join("../test_output_data", "receipt_xml_simple_to_dcr_js_portal.xml")
        pm4py.write_dcr_xml(dcr_graph=dcr,path=path,variant=dcr_exporter.Variants.DCR_JS_PORTAL, dcr_title='receipt_xml_simple_to_dcr_js_portal')

    def test_exporter_to_dcr_portal(self):
        event_log_file = os.path.join("../input_data", "sepsis", "data", "Sepsis Cases - Event Log.xes")
        dcrxml_file_export = os.path.join("../test_output_data", "sepsis_dcr_portal.xml")
        log = pm4py.read_xes(event_log_file)
        dcr, _ = disc_alg.apply(log)
        pm4py.write_dcr_xml(dcr_graph=dcr,path=dcrxml_file_export,variant=dcr_exporter.XML_DCR_PORTAL, dcr_title='xml_2_dcr_portal')

    def test_importer_from_dcr_portal(self):
        dcr = pm4py.read_dcr_xml(os.path.join("../test_output_data", "sepsis_dcr_portal.xml"))
        self.assertIsNotNone(dcr)

    def test_import_export_dcr_portal(self):
        dcr = pm4py.read_dcr_xml(os.path.join("../test_output_data", "sepsis_dcr_portal.xml"))
        path = os.path.join("../test_output_data", "sepsis_dcr_portal_exported.xml")
        pm4py.write_dcr_xml(dcr_graph=dcr,path=path,variant=dcr_exporter.XML_DCR_PORTAL, dcr_title='sepsis_dcr_portal_exported_xml')
        dcr_imported_after_export = pm4py.read_dcr_xml(path)
        self.assertEqual(len(dcr.__dict__), len(dcr_imported_after_export.__dict__))
        os.remove(path)

    def test_exporter_to_dcr_js_portal(self):
        event_log_file = os.path.join("../input_data", "receipt.xes")
        dcrxml_file_export = os.path.join("../test_output_data", "receipt_dcr_js_portal.xml")
        log = pm4py.read_xes(event_log_file)
        dcr, _ = disc_alg.apply(log)
        pm4py.write_dcr_xml(dcr_graph=dcr, path=dcrxml_file_export, variant=dcr_exporter.Variants.DCR_JS_PORTAL, dcr_title='reviewing_exported_dcr_js_portal')

    def test_importer_from_dcr_js_portal(self):
        dcr = pm4py.read_dcr_xml(os.path.join("../test_output_data", "receipt_dcr_js_portal.xml"))
        self.assertIsNotNone(dcr)

    def test_import_export_dcr_js_portal(self):
        dcr = pm4py.read_dcr_xml(os.path.join("../test_output_data", "receipt_dcr_js_portal.xml"))
        path = os.path.join("../test_output_data", "receipt_dcr_js_portal_exported.xml")
        pm4py.write_dcr_xml(dcr_graph=dcr,path=path,variant=dcr_exporter.DCR_JS_PORTAL, dcr_title='receipt_dcr_js_portal_exported')
        dcr_imported_after_export = pm4py.read_dcr_xml(path)
        self.assertEqual(len(dcr.__dict__), len(dcr_imported_after_export.__dict__))
        os.remove(path)

    def test_xml_dcr_portal_to_dcr_js_portal(self):
        dcr = pm4py.read_dcr_xml(os.path.join("../test_output_data", "sepsis_dcr_portal.xml"))
        path = os.path.join("../test_output_data", "sepsis_dcr_js_portal.xml")
        pm4py.write_dcr_xml(dcr_graph=dcr,path=path,variant=dcr_exporter.DCR_JS_PORTAL, dcr_title='sepsis_dcr_js_portal')

    def test_dcr_js_portal_to_xml_dcr_portal(self):
        dcr = pm4py.read_dcr_xml(os.path.join("../test_output_data", "receipt_dcr_js_portal.xml"))
        path = os.path.join("../test_output_data", "receipt_dcr_xml_portal.xml")
        pm4py.write_dcr_xml(dcr_graph=dcr,path=path,variant=dcr_exporter.XML_DCR_PORTAL, dcr_title='receipt_dcr_xml_portal')

    def test_xes_to_xml_dcr_portal_to_dcr_js_portal(self):
        event_log_file = os.path.join("../input_data", "running-example.xes")
        dcrxml_file_export = os.path.join("../test_output_data", "running-example_dcr_portal.xml")
        log = pm4py.read_xes(event_log_file)
        dcr, _ = disc_alg.apply(log)
        pm4py.write_dcr_xml(dcr_graph=dcr,path=dcrxml_file_export,variant=dcr_exporter.XML_DCR_PORTAL, dcr_title='running-example_dcr_portal')
        dcr_imported_after_export = pm4py.read_dcr_xml(dcrxml_file_export)
        path = os.path.join("../test_output_data", "running-example_dcr_js_portal.xml")
        pm4py.write_dcr_xml(dcr_graph=dcr_imported_after_export,path=path,variant=dcr_exporter.DCR_JS_PORTAL, dcr_title='running-example_dcr_js_portal')
        os.remove(dcrxml_file_export)


if __name__ == '__main__':
    unittest.main()

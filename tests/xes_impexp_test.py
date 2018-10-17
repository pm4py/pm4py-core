from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.log.exporter.xes import factory as xes_exporter
from pm4py.objects.log.importer.csv import factory as csv_importer
from pm4py.objects.log.exporter.csv import factory as csv_exporter
import pm4py.objects.log.transform as log_transform
from tests.constants import INPUT_DATA_DIR, OUTPUT_DATA_DIR, PROBLEMATIC_XES_DIR, COMPRESSED_INPUT_DATA
import logging
import unittest
import os


class XesImportExportTest(unittest.TestCase):
    def test_importExportXEStoXES(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        trace_log = xes_importer.import_log(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        xes_exporter.export_log(trace_log, os.path.join(OUTPUT_DATA_DIR, "running-example-exported.xes"))
        trace_log_imported_after_export = xes_importer.import_log(
            os.path.join(OUTPUT_DATA_DIR, "running-example-exported.xes"))
        self.assertEqual(len(trace_log), len(trace_log_imported_after_export))
        os.remove(os.path.join(OUTPUT_DATA_DIR, "running-example-exported.xes"))

    def test_importExportXEStoCSV(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        trace_log = xes_importer.import_log(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        event_log = log_transform.transform_trace_log_to_event_log(trace_log)
        csv_exporter.export_log(event_log, os.path.join(OUTPUT_DATA_DIR, "running-example-exported.csv"))
        event_log_imported_after_export = csv_importer.import_log(
            os.path.join(OUTPUT_DATA_DIR, "running-example-exported.csv"))
        trace_log_imported_after_export = log_transform.transform_event_log_to_trace_log(event_log_imported_after_export)
        self.assertEqual(len(trace_log), len(trace_log_imported_after_export))
        os.remove(os.path.join(OUTPUT_DATA_DIR, "running-example-exported.csv"))

    def test_importExportProblematicLogs(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        logs = os.listdir(PROBLEMATIC_XES_DIR)
        for log in logs:
            log_full_path = os.path.join(PROBLEMATIC_XES_DIR, log)
            try:
                output_log_path = os.path.join(OUTPUT_DATA_DIR, log)
                trace_log = xes_importer.import_log(log_full_path)
                xes_exporter.export_log(trace_log, output_log_path)
                trace_log_imported_after_export = xes_importer.import_log(output_log_path)
                self.assertEqual(len(trace_log), len(trace_log_imported_after_export))
                os.remove(output_log_path)
            except SyntaxError as e:
                logging.info("SyntaxError on log " + str(log) + ": " + str(e))

    def test_importExportXESfromGZIP_imp1(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        trace_log = xes_importer.import_log(os.path.join(COMPRESSED_INPUT_DATA, "01_running-example.xes.gz"))
        xes_exporter.export_log(trace_log, os.path.join(OUTPUT_DATA_DIR, "01-running-example.xes"),
                                parameters={"compress": True})
        os.remove(os.path.join(OUTPUT_DATA_DIR, "01-running-example.xes.gz"))

    def test_importXESfromGZIP_imp2(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        trace_log = xes_importer.import_log(os.path.join(COMPRESSED_INPUT_DATA, "01_running-example.xes.gz"))
        del trace_log


if __name__ == "__main__":
    unittest.main()

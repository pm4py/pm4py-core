from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.log.exporter.xes import factory as xes_exporter
from pm4py.objects.log.importer.csv import factory as csv_importer
from pm4py.objects.log.exporter.csv import factory as csv_exporter
from pm4py.objects.conversion.log import factory as log_conv_fact
from tests.constants import INPUT_DATA_DIR, OUTPUT_DATA_DIR, PROBLEMATIC_XES_DIR, COMPRESSED_INPUT_DATA
import logging
import unittest
import os


class XesImportExportTest(unittest.TestCase):
    def test_importExportXEStoXES(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log = xes_importer.import_log(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        xes_exporter.export_log(log, os.path.join(OUTPUT_DATA_DIR, "running-example-exported.xes"))
        log_imported_after_export = xes_importer.import_log(
            os.path.join(OUTPUT_DATA_DIR, "running-example-exported.xes"))
        self.assertEqual(len(log), len(log_imported_after_export))
        os.remove(os.path.join(OUTPUT_DATA_DIR, "running-example-exported.xes"))

    def test_importExportXEStoCSV(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log = xes_importer.import_log(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        event_log = log_conv_fact.apply(log, variant=log_conv_fact.TO_EVENT_STREAM)
        csv_exporter.export(event_log, os.path.join(OUTPUT_DATA_DIR, "running-example-exported.csv"))
        event_log_newimport = csv_importer.import_event_stream(
            os.path.join(OUTPUT_DATA_DIR, "running-example-exported.csv"))
        log_imported_after_export = log_conv_fact.apply(event_log_newimport)
        self.assertEqual(len(log), len(log_imported_after_export))
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
                log = xes_importer.import_log(log_full_path)
                xes_exporter.export_log(log, output_log_path)
                log_imported_after_export = xes_importer.import_log(output_log_path)
                self.assertEqual(len(log), len(log_imported_after_export))
                os.remove(output_log_path)
            except SyntaxError as e:
                logging.info("SyntaxError on log " + str(log) + ": " + str(e))

    def test_importExportXESfromGZIP_imp1(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log = xes_importer.import_log(os.path.join(COMPRESSED_INPUT_DATA, "01_running-example.xes.gz"))
        xes_exporter.export_log(log, os.path.join(OUTPUT_DATA_DIR, "01-running-example.xes"),
                                parameters={"compress": True})
        os.remove(os.path.join(OUTPUT_DATA_DIR, "01-running-example.xes.gz"))

    def test_importXESfromGZIP_imp2(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log = xes_importer.import_log(os.path.join(COMPRESSED_INPUT_DATA, "01_running-example.xes.gz"))
        del log


if __name__ == "__main__":
    unittest.main()

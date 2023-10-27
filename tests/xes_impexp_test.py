from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from tests.constants import INPUT_DATA_DIR, OUTPUT_DATA_DIR, PROBLEMATIC_XES_DIR, COMPRESSED_INPUT_DATA
import logging
import unittest
import os


class XesImportExportTest(unittest.TestCase):
    def test_importExportXEStoXES(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log = xes_importer.apply(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        xes_exporter.apply(log, os.path.join(OUTPUT_DATA_DIR, "running-example-exported.xes"))
        log_imported_after_export = xes_importer.apply(
            os.path.join(OUTPUT_DATA_DIR, "running-example-exported.xes"))
        self.assertEqual(len(log), len(log_imported_after_export))
        os.remove(os.path.join(OUTPUT_DATA_DIR, "running-example-exported.xes"))

    def test_importExportProblematicLogs(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        logs = os.listdir(PROBLEMATIC_XES_DIR)
        for log_name in logs:
            log_full_path = os.path.join(PROBLEMATIC_XES_DIR, log_name)
            try:
                output_log_path = os.path.join(OUTPUT_DATA_DIR, log_name)
                log = xes_importer.apply(log_full_path)
                xes_exporter.apply(log, output_log_path)
                log_imported_after_export = xes_importer.apply(output_log_path)
                self.assertEqual(len(log), len(log_imported_after_export))
                os.remove(output_log_path)
            except SyntaxError as e:
                logging.info("SyntaxError on log " + str(log_name) + ": " + str(e))

    def test_importExportXESfromGZIP_imp1(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log = xes_importer.apply(os.path.join(COMPRESSED_INPUT_DATA, "01_running-example.xes.gz"))
        xes_exporter.apply(log, os.path.join(OUTPUT_DATA_DIR, "01-running-example.xes"),
                           parameters={xes_exporter.Variants.ETREE.value.Parameters.COMPRESS: True})
        os.remove(os.path.join(OUTPUT_DATA_DIR, "01-running-example.xes.gz"))

    def test_importXESfromGZIP_imp2(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log = xes_importer.apply(os.path.join(COMPRESSED_INPUT_DATA, "01_running-example.xes.gz"))
        del log


if __name__ == "__main__":
    unittest.main()

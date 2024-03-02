from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from tests.constants import (
    INPUT_DATA_DIR,
    OUTPUT_DATA_DIR,
)
from deepdiff import DeepDiff
import unittest
import os


class XesCompositeListAttributesTest(unittest.TestCase):
    def test_minimalXESCompositeListAttributes(self):
        xes_log_path = os.path.join(INPUT_DATA_DIR, "composite_list_attributes.xes")
        exported_log_path = os.path.join(
            OUTPUT_DATA_DIR, "composite_list_attributes.xes"
        )
        log = xes_importer.apply(
            xes_log_path,
        )

        xes_exporter.apply(log, exported_log_path)
        log_imported_after_export = xes_importer.apply(exported_log_path)

        self.check_difference(log, log_imported_after_export)

        os.remove(exported_log_path)

    def check_difference(self, log_1, log_2):
        difference = self.compare_logs(log_1, log_2)

        if difference:
            self.fail(f"Logs do not match with difference: {difference}")

    def compare_logs(self, log_1, log_2):
        diff = DeepDiff(log_1, log_2, ignore_order=True)
        if diff:
            return diff


if __name__ == "__main__":
    unittest.main()

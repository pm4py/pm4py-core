from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.exporter.xes import exporter as xes_exporter

from pm4py.objects.log.importer.yaml import importer as yaml_importer
from pm4py.objects.log.exporter.yaml import exporter as yaml_exporter

from pm4py.util import constants


from tests.constants import INPUT_DATA_DIR, OUTPUT_DATA_DIR, COMPRESSED_INPUT_DATA
import unittest
import os
from deepdiff import DeepDiff


class XesYamlTest(unittest.TestCase):
    # ======================================== importExportYAMLtoYAML test cases ========================================
    def test_importExportYAMLtoYAML_running_example(self):
        self.perform_importExportYAMLtoYAML("running-example")

    # ======================================== importExportXEStoYAML test cases ========================================
    def test_importExportXEStoYAML_running_example(self):
        self.perform_importExportXEStoYAML("running-example")

    # ======================================== importExportYAMLtoXES test cases ========================================
    def test_importExportYAMLtoXES_running_example(self):
        self.perform_importExportYAMLtoXES("running-example")

    # ======================================== zipped XES-YAML test cases ========================================
    def test_importExportYAML_fromGZIP_running_example(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        file_name = "chess_production.xes.yaml.gz"
        log = yaml_importer.apply(os.path.join(COMPRESSED_INPUT_DATA, file_name))
        yaml_exporter.apply(
            log,
            os.path.join(OUTPUT_DATA_DIR, file_name),
            parameters={
                yaml_exporter.yaml_dumper.Parameters.COMPRESS: True,
            },
        )
        os.remove(os.path.join(OUTPUT_DATA_DIR, file_name))

    # ====================================================================================================================

    def check_difference(self, log_1, log_2):
        difference = self.compare_logs(log_1, log_2)

        if difference:
            self.fail(f"Logs do not match with difference:\n{difference}")

    def compare_logs(self, log_1, log_2):
        diff = DeepDiff(log_1, log_2, ignore_order=True)
        if diff:
            return diff

    def perform_importExportXEStoXES(self, log_file_path: str):
        xes_log_path = os.path.join(INPUT_DATA_DIR, f"{log_file_path}.xes")
        exported_xes_log_path = os.path.join(
            OUTPUT_DATA_DIR, f"{log_file_path}_exported.xes"
        )

        xes_log = xes_importer.apply(xes_log_path)

        parameters = {constants.PARAMETER_CONSTANT_CASEID_KEY: "cpee:instance"}

        xes_exporter.apply(
            xes_log,
            exported_xes_log_path,
            parameters=parameters,
        )

        xes_log_after_export = xes_importer.apply(exported_xes_log_path)

        self.check_difference(xes_log, xes_log_after_export)

        os.remove(exported_xes_log_path)

    def perform_importExportYAMLtoYAML(self, log_file_path: str):
        yaml_log_path = os.path.join(INPUT_DATA_DIR, f"{log_file_path}.xes.yaml")
        exported_yaml_log_path = os.path.join(
            OUTPUT_DATA_DIR, f"{log_file_path}_exported.xes.yaml"
        )

        yaml_log = yaml_importer.apply(yaml_log_path)

        parameters = {constants.PARAMETER_CONSTANT_CASEID_KEY: "cpee:instance"}

        yaml_exporter.apply(
            yaml_log,
            exported_yaml_log_path,
            parameters=parameters,
            log_header=yaml_importer.get_log_header(yaml_log_path),
        )

        yaml_log_after_export = yaml_importer.apply(exported_yaml_log_path)

        self.check_difference(yaml_log, yaml_log_after_export)

        os.remove(exported_yaml_log_path)

    def perform_importExportXEStoYAML(self, log_file_path: str):
        xes_log_path = os.path.join(INPUT_DATA_DIR, f"{log_file_path}.xes")
        exported_yaml_log_path = os.path.join(
            OUTPUT_DATA_DIR, f"{log_file_path}_exported.xes.yaml"
        )

        xes_log = xes_importer.apply(xes_log_path)

        yaml_exporter.apply(
            xes_log,
            exported_yaml_log_path,
        )

        yaml_log_after_export = yaml_importer.apply(exported_yaml_log_path)

        self.check_difference(xes_log, yaml_log_after_export)

        os.remove(exported_yaml_log_path)

    def perform_importExportYAMLtoXES(self, log_file_path: str):
        yaml_log_path = os.path.join(INPUT_DATA_DIR, f"{log_file_path}.xes.yaml")
        exported_xes_log_path = os.path.join(
            OUTPUT_DATA_DIR, f"{log_file_path}_exported.xes"
        )

        yaml_log = yaml_importer.apply(yaml_log_path)

        xes_exporter.apply(
            yaml_log,
            exported_xes_log_path,
            parameters={constants.PARAMETER_CONSTANT_CASEID_KEY: "cpee:instance"},
        )

        xes_log_after_export = xes_importer.apply(exported_xes_log_path)

        self.check_difference(yaml_log, xes_log_after_export)

        os.remove(exported_xes_log_path)


if __name__ == "__main__":
    unittest.main()

import unittest
import pm4py
import os


class OcelFilteringTest(unittest.TestCase):
    def test_ocel_import_csv_export_csv(self):
        input_path = os.path.join("input_data", "ocel", "example_log.csv")
        output_path = os.path.join("test_output_data", "example_log.csv")
        ocel = pm4py.read_ocel(input_path)
        pm4py.write_ocel(ocel, output_path)
        os.remove(output_path)

    def test_ocel_import_csv_export_jsonocel(self):
        input_path = os.path.join("input_data", "ocel", "example_log.csv")
        output_path = os.path.join("test_output_data", "example_log.jsonocel")
        ocel = pm4py.read_ocel(input_path)
        pm4py.write_ocel(ocel, output_path)
        os.remove(output_path)

    def test_ocel_import_csv_export_xmlocel(self):
        input_path = os.path.join("input_data", "ocel", "example_log.csv")
        output_path = os.path.join("test_output_data", "example_log.xmlocel")
        ocel = pm4py.read_ocel(input_path)
        pm4py.write_ocel(ocel, output_path)
        os.remove(output_path)

    def test_ocel_import_jsonocel_export_csv(self):
        input_path = os.path.join("input_data", "ocel", "example_log.jsonocel")
        output_path = os.path.join("test_output_data", "example_log.csv")
        ocel = pm4py.read_ocel(input_path)
        pm4py.write_ocel(ocel, output_path)
        os.remove(output_path)

    def test_ocel_import_jsonocel_export_jsonocel(self):
        input_path = os.path.join("input_data", "ocel", "example_log.jsonocel")
        output_path = os.path.join("test_output_data", "example_log.jsonocel")
        ocel = pm4py.read_ocel(input_path)
        pm4py.write_ocel(ocel, output_path)
        os.remove(output_path)

    def test_ocel_import_jsonocel_export_xmlocel(self):
        input_path = os.path.join("input_data", "ocel", "example_log.jsonocel")
        output_path = os.path.join("test_output_data", "example_log.xmlocel")
        ocel = pm4py.read_ocel(input_path)
        pm4py.write_ocel(ocel, output_path)
        os.remove(output_path)

    def test_ocel_import_xmlocel_export_csv(self):
        input_path = os.path.join("input_data", "ocel", "example_log.xmlocel")
        output_path = os.path.join("test_output_data", "example_log.csv")
        ocel = pm4py.read_ocel(input_path)
        pm4py.write_ocel(ocel, output_path)
        os.remove(output_path)

    def test_ocel_import_xmlocel_export_jsonocel(self):
        input_path = os.path.join("input_data", "ocel", "example_log.xmlocel")
        output_path = os.path.join("test_output_data", "example_log.jsonocel")
        ocel = pm4py.read_ocel(input_path)
        pm4py.write_ocel(ocel, output_path)
        os.remove(output_path)

    def test_ocel_import_xmlocel_export_xmlocel(self):
        input_path = os.path.join("input_data", "ocel", "example_log.xmlocel")
        output_path = os.path.join("test_output_data", "example_log.xmlocel")
        ocel = pm4py.read_ocel(input_path)
        pm4py.write_ocel(ocel, output_path)
        os.remove(output_path)


if __name__ == "__main__":
    unittest.main()

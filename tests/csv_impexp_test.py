import os
import unittest

import pm4py.objects.log.transform as log_transform
from pm4py.objects.log.exporter.csv import factory as csv_exporter
from pm4py.objects.log.exporter.xes import factory as xes_exporter
from pm4py.objects.log.importer.csv import factory as csv_importer
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.log.util import sampling, sorting, index_attribute
from tests.constants import INPUT_DATA_DIR, OUTPUT_DATA_DIR


class CsvImportExportTest(unittest.TestCase):
    def test_importExportCSVtoXES(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        event_log = csv_importer.import_event_stream(os.path.join(INPUT_DATA_DIR, "running-example.csv"))
        event_log = sorting.sort_timestamp(event_log)
        event_log = sampling.sample(event_log)
        event_log = index_attribute.insert_event_index_as_event_attribute(event_log)
        log = log_transform.transform_event_stream_to_event_log(event_log)
        log = sorting.sort_timestamp(log)
        log = sampling.sample(log)
        log = index_attribute.insert_trace_index_as_event_attribute(log)
        xes_exporter.export_log(log, os.path.join(OUTPUT_DATA_DIR, "running-example-exported.xes"))
        log_imported_after_export = xes_importer.import_log(
            os.path.join(OUTPUT_DATA_DIR, "running-example-exported.xes"))
        self.assertEqual(len(log), len(log_imported_after_export))
        os.remove(os.path.join(OUTPUT_DATA_DIR, "running-example-exported.xes"))

    def test_importExportCSVtoCSV(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        event_log = csv_importer.import_event_stream(os.path.join(INPUT_DATA_DIR, "running-example.csv"))
        event_log = sorting.sort_timestamp(event_log)
        event_log = sampling.sample(event_log)
        event_log = index_attribute.insert_event_index_as_event_attribute(event_log)
        log = log_transform.transform_event_stream_to_event_log(event_log)
        log = sorting.sort_timestamp(log)
        log = sampling.sample(log)
        log = index_attribute.insert_trace_index_as_event_attribute(log)
        event_log_transformed = log_transform.transform_event_log_to_event_stream(log)
        csv_exporter.export(event_log_transformed, os.path.join(OUTPUT_DATA_DIR, "running-example-exported.csv"))
        event_log_imported_after_export = csv_importer.import_event_stream(
            os.path.join(OUTPUT_DATA_DIR, "running-example-exported.csv"))
        log_imported_after_export = log_transform.transform_event_stream_to_event_log(
            event_log_imported_after_export)
        self.assertEqual(len(log), len(log_imported_after_export))
        os.remove(os.path.join(OUTPUT_DATA_DIR, "running-example-exported.csv"))


if __name__ == "__main__":
    unittest.main()

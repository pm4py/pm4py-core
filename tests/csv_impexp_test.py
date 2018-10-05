import unittest
import os, sys, inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from pm4py.entities.log.importer.xes import factory as xes_importer
from pm4py.entities.log.exporter.xes import factory as xes_exporter
from pm4py.entities.log.importer.csv import factory as csv_importer
from pm4py.entities.log.exporter.csv import factory as csv_exporter
import pm4py.entities.log.transform as log_transform
from tests.constants import INPUT_DATA_DIR, OUTPUT_DATA_DIR


class CsvImportExportTest(unittest.TestCase):
    def test_importExportCSVtoXES(self):
        eventLog = csv_importer.import_log(os.path.join(INPUT_DATA_DIR, "running-example.csv"))
        eventLog.sort()
        eventLog.sample()
        eventLog.insert_event_index_as_event_attribute()
        traceLog = log_transform.transform_event_log_to_trace_log(eventLog)
        traceLog.sort()
        traceLog.sample()
        traceLog.insert_trace_index_as_event_attribute()
        xes_exporter.export_log(traceLog, os.path.join(OUTPUT_DATA_DIR, "running-example-exported.xes"))
        traceLogImportedAfterExport = xes_importer.import_log(
            os.path.join(OUTPUT_DATA_DIR, "running-example-exported.xes"))
        self.assertEqual(len(traceLog), len(traceLogImportedAfterExport))
        os.remove(os.path.join(OUTPUT_DATA_DIR, "running-example-exported.xes"))

    def test_importExportCSVtoCSV(self):
        eventLog = csv_importer.import_log(os.path.join(INPUT_DATA_DIR, "running-example.csv"))
        eventLog.sort()
        eventLog.sample()
        eventLog.insert_event_index_as_event_attribute()
        traceLog = log_transform.transform_event_log_to_trace_log(eventLog)
        traceLog.sort()
        traceLog.sample()
        traceLog.insert_trace_index_as_event_attribute()
        eventLogTransformed = log_transform.transform_trace_log_to_event_log(traceLog)
        csv_exporter.export_log(eventLogTransformed, os.path.join(OUTPUT_DATA_DIR, "running-example-exported.csv"))
        eventLogImportedAfterExport = csv_importer.import_log(
            os.path.join(OUTPUT_DATA_DIR, "running-example-exported.csv"))
        traceLogImportedAfterExport = log_transform.transform_event_log_to_trace_log(eventLogImportedAfterExport)
        self.assertEqual(len(traceLog), len(traceLogImportedAfterExport))
        os.remove(os.path.join(OUTPUT_DATA_DIR, "running-example-exported.csv"))


if __name__ == "__main__":
    unittest.main()

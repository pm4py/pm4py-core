import unittest
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from pm4py.log.importer import xes as xes_importer
from pm4py.log.exporter import xes as xes_exporter
from pm4py.log.importer import csv as csv_importer
from pm4py.log.exporter import csv as csv_exporter
import pm4py.log.transform as log_transform
from constants import INPUT_DATA_DIR, OUTPUT_DATA_DIR

class XesImportExportTest(unittest.TestCase):
	def test_importExportXEStoXES(self):
		traceLog = xes_importer.import_from_path_xes(os.path.join(INPUT_DATA_DIR,"running-example.xes"))
		xes_exporter.export_log(traceLog, os.path.join(OUTPUT_DATA_DIR,"running-example-exported.xes"))
		traceLogImportedAfterExport = xes_importer.import_from_path_xes(os.path.join(OUTPUT_DATA_DIR,"running-example-exported.xes"))
		self.assertEqual(len(traceLog),len(traceLogImportedAfterExport))
		os.remove(os.path.join(OUTPUT_DATA_DIR,"running-example-exported.xes"))
	
	def test_importExportXEStoCSV(self):
		traceLog = xes_importer.import_from_path_xes(os.path.join(INPUT_DATA_DIR,"running-example.xes"))
		eventLog = log_transform.transform_trace_log_to_event_log(traceLog)
		csv_exporter.export_log(eventLog, os.path.join(OUTPUT_DATA_DIR,"running-example-exported.csv"))
		eventLogImportedAfterExport = csv_importer.import_from_path(os.path.join(OUTPUT_DATA_DIR,"running-example-exported.csv"))
		traceLogImportedAfterExport = log_transform.transform_event_log_to_trace_log(eventLogImportedAfterExport)
		self.assertEqual(len(traceLog), len(traceLogImportedAfterExport))
		os.remove(os.path.join(OUTPUT_DATA_DIR,"running-example-exported.csv"))

if __name__ == "__main__":
	unittest.main()
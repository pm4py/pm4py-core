import unittest
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from tests.constants import INPUT_DATA_DIR
from pm4py.log.importer import xes as xes_importer
from pm4py.filtering.paths import paths_filter
from pm4py.filtering.start_activities import start_activities_filter
from pm4py.filtering.attributes import attributes_filter
from pm4py.filtering.end_activities import end_activities_filter
from pm4py.filtering.variants import variants_filter as variants_module


class LogFilteringTest(unittest.TestCase):
    def test_logfiltering_filtering1(self):
        inputLog = os.path.join(INPUT_DATA_DIR, "running-example.xes")
        log = xes_importer.import_from_file_xes(inputLog)
        log = attributes_filter.apply_auto_filter(log)
        log = variants_module.apply_auto_filter(log)
        log = start_activities_filter.apply_auto_filter(log)
        log = end_activities_filter.apply_auto_filter(log)
        log = paths_filter.apply_auto_filter(log)

if __name__ == "__main__":
    unittest.main()
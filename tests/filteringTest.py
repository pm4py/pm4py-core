import unittest
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from tests.constants import INPUT_DATA_DIR
from pm4py.log.importer import xes as xes_importer
from pm4py.log.util import activities, end_activities, paths, start_activities
from pm4py.log.util import variants as variants_module

class LogFilteringTest(unittest.TestCase):
    def test_logfiltering_filtering1(self):
        inputLog = os.path.join(INPUT_DATA_DIR, "running-example.xes")
        log = xes_importer.import_from_file_xes(inputLog)
        log = activities.apply_auto_filter(log)
        log = variants_module.apply_auto_filter(log)
        log = start_activities.apply_auto_filter(log)
        log = end_activities.apply_auto_filter(log)
        log = paths.apply_auto_filter(log)

if __name__ == "__main__":
    unittest.main()
import unittest
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from tests.constants import INPUT_DATA_DIR
from pm4py import log as log_lib
from pm4py.models.transition_system import visualize as ts_viz
from pm4py.log.importer.xes import factory as xes_importer

class TransitionSystemTest(unittest.TestCase):
    def test_transitionsystem1(self):
        from pm4py.algo.transition_system.versions import view_based as ts

        inputLog = os.path.join(INPUT_DATA_DIR, "running-example.xes")
        log = xes_importer.import_log(inputLog)
        ts = ts.apply(log, parameters={ts.PARAM_KEY_VIEW: ts.VIEW_SEQUENCE, ts.PARAM_KEY_WINDOW: 3,
                                       ts.PARAM_KEY_DIRECTION: ts.DIRECTION_FORWARD})
        viz = ts_viz.graphviz.visualize(ts)

if __name__ == "__main__":
    unittest.main()
import unittest
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
import pm4py
from tests.constants import INPUT_DATA_DIR
from pm4py.entities.log.importer.xes import factory as xes_importer
from pm4py.algo.discovery.transition_system import factory as ts_factory
from pm4py.algo.discovery.transition_system import parameters

class TransitionSystemTest(unittest.TestCase):
    def test_transitionsystem1(self):
        inputLog = os.path.join(INPUT_DATA_DIR, "running-example.xes")
        log = xes_importer.import_log(inputLog)
        ts = ts_factory.apply(log, parameters={parameters.PARAM_KEY_VIEW: parameters.VIEW_SEQUENCE, parameters.PARAM_KEY_WINDOW: 3,
                                               parameters.PARAM_KEY_DIRECTION: parameters.DIRECTION_FORWARD})
        viz = pm4py.visualization.transition_system.util.visualize_graphviz.visualize(ts)

if __name__ == "__main__":
    unittest.main()
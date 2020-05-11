import pm4py
from tests.constants import INPUT_DATA_DIR
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.algo.discovery.transition_system import factory as ts_factory
from pm4py.algo.discovery.transition_system import parameters
import unittest
import os


class TransitionSystemTest(unittest.TestCase):
    def test_transitionsystem1(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        input_log = os.path.join(INPUT_DATA_DIR, "running-example.xes")
        log = xes_importer.import_log(input_log)
        ts = ts_factory.apply(log, parameters={parameters.PARAM_KEY_VIEW: parameters.VIEW_SEQUENCE,
                                               parameters.PARAM_KEY_WINDOW: 3,
                                               parameters.PARAM_KEY_DIRECTION: parameters.DIRECTION_FORWARD})
        viz = pm4py.visualization.transition_system.util.visualize_graphviz.visualize(ts)
        del viz


if __name__ == "__main__":
    unittest.main()

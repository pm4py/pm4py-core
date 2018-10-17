from tests.constants import INPUT_DATA_DIR
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.evaluation.precision import factory as etc_factory
from pm4py.algo.discovery.inductive.versions.dfg import dfg_only
import unittest
import os

class ETCTest(unittest.TestCase):
    def test_etc1(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log = xes_importer.import_log(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        net, marking, final_marking = dfg_only.apply(log, None)
        precision = etc_factory.apply(log, net, marking, final_marking)
        del precision


if __name__ == "__main__":
    unittest.main()

import os
import unittest

from pm4py.algo.discovery.inductive import factory as inductive_miner
from pm4py.evaluation.precision import factory as etc_factory
from pm4py.objects.log.importer.xes import factory as xes_importer
from tests.constants import INPUT_DATA_DIR


class ETCTest(unittest.TestCase):
    def test_etc1(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log = xes_importer.import_log(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        net, marking, final_marking = inductive_miner.apply(log)
        precision = etc_factory.apply(log, net, marking, final_marking)
        del precision


if __name__ == "__main__":
    unittest.main()

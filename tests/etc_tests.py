import os
import unittest

from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.evaluation.precision import algorithm as etc_alg
from pm4py.objects.log.importer.xes import importer as xes_importer
from tests.constants import INPUT_DATA_DIR


class ETCTest(unittest.TestCase):
    def test_etc1(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log = xes_importer.apply(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        net, marking, final_marking = inductive_miner.apply(log)
        precision = etc_alg.apply(log, net, marking, final_marking, variant=etc_alg.ETCONFORMANCE_TOKEN)
        del precision


if __name__ == "__main__":
    unittest.main()

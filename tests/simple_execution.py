import os
import unittest

from pm4py.algo.discovery.simple.model.log import factory as simple_model_factory
from pm4py.objects.log.importer.xes import factory as xes_importer
from tests.constants import INPUT_DATA_DIR


class SimpleExecutionTest(unittest.TestCase):
    def test_simple_execution_receipt(self):
        self.dummy = "dummy"
        log = xes_importer.apply(os.path.join(INPUT_DATA_DIR, "receipt.xes"))
        output_dictionary = simple_model_factory.apply(log)
        net, initial_marking, final_marking = simple_model_factory.apply(log, classic_output=True)
        del output_dictionary
        del net
        del initial_marking
        del final_marking


if __name__ == "__main__":
    unittest.main()

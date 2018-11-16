import os
import unittest

from pm4py.algo.discovery.inductive import factory as inductive_miner
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.visualization.process_tree import factory as pt_vis_factory
from tests.constants import INPUT_DATA_DIR


class InductiveMinerDFTest(unittest.TestCase):
    def test_tree_running_example(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log = xes_importer.import_log(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        tree = inductive_miner.apply_tree(log)
        gviz = pt_vis_factory.apply(tree)
        del gviz
        # test log generation
        log = tree.generate_log()
        del log

    def test_tree_receipt(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log = xes_importer.import_log(os.path.join(INPUT_DATA_DIR, "receipt.xes"))
        tree = inductive_miner.apply_tree(log)
        gviz = pt_vis_factory.apply(tree)
        del gviz
        # test log generation
        log = tree.generate_log()
        del log


if __name__ == "__main__":
    unittest.main()

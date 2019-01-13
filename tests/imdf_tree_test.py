import os
import unittest

from pm4py.algo.discovery.inductive import factory as inductive_miner
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.visualization.process_tree import factory as pt_vis_factory
from pm4py.objects.process_tree import semantics as pt_semantics
from pm4py.objects.process_tree import util as pt_util
from tests.constants import INPUT_DATA_DIR


class InductiveMinerDFTreeTest(unittest.TestCase):
    def test_tree_running_example(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log = xes_importer.import_log(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        tree = inductive_miner.apply_tree(log)
        gviz = pt_vis_factory.apply(tree)
        del gviz
        # test log generation
        log = pt_semantics.generate_log(tree)
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
        log = pt_semantics.generate_log(tree)
        del log

    def test_tree_parsing(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        tree = pt_util.parse("->(X('a', 'b', tau), +('c', 'd'))")
        # test log generation
        log = pt_semantics.generate_log(tree)

if __name__ == "__main__":
    unittest.main()

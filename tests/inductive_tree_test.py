import os
import unittest

from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.visualization.process_tree import visualizer as pt_vis
from pm4py.objects.process_tree import semantics as pt_semantics
from pm4py.objects.process_tree.utils import generic as pt_util
from tests.constants import INPUT_DATA_DIR


class InductiveMinerTreeTest(unittest.TestCase):
    def test_tree_running_example_log_plain_based(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log = xes_importer.apply(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        tree = inductive_miner.apply(log, variant=inductive_miner.Variants.IM)
        gviz = pt_vis.apply(tree)
        del gviz
        # test log generation
        log = pt_semantics.generate_log(tree)
        del log

    def test_tree_receipt_log_plain_based(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log = xes_importer.apply(os.path.join(INPUT_DATA_DIR, "receipt.xes"))
        tree = inductive_miner.apply(log, variant=inductive_miner.Variants.IM)
        gviz = pt_vis.apply(tree)
        del gviz
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

import unittest
import os, sys, inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from pm4py.objects.log.importer.csv import factory as csv_importer
from pm4py.objects.log.importer.xes import factory as xes_importer
import pm4py.objects.log.transform as log_transform
from pm4py.algo.discovery.inductive import factory as inductive_miner
from pm4py.visualization.petrinet.common import visualize as pn_viz
from pm4py.algo.conformance.tokenreplay.versions import token_replay
from pm4py.algo.conformance.tokenreplay.versions.token_replay import NoConceptNameException
from pm4py.objects import petri
from pm4py.objects.petri.exporter import pnml as petri_exporter
from tests.constants import INPUT_DATA_DIR, OUTPUT_DATA_DIR, PROBLEMATIC_XES_DIR
from pm4py.algo.discovery.dfg.versions import native as dfg_inst
import logging
from pm4py.visualization.process_tree import factory as pt_vis_factory

class InductiveMinerDFTest(unittest.TestCase):
    def test_tree_running_example(self):
        log = xes_importer.import_log(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        tree = inductive_miner.apply_tree(log)
        gviz = pt_vis_factory.apply(tree)

    def test_tree_receipt(self):
        log = xes_importer.import_log(os.path.join(INPUT_DATA_DIR, "receipt.xes"))
        tree = inductive_miner.apply_tree(log)
        gviz = pt_vis_factory.apply(tree)

if __name__ == "__main__":
    unittest.main()
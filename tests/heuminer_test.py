import os
import unittest

from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
from pm4py.objects.log.adapters.pandas import csv_import_adapter
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.visualization.heuristics_net import visualizer as hn_vis
from pm4py.visualization.petrinet import visualizer as pn_vis
from tests.constants import INPUT_DATA_DIR


class HeuMinerTest(unittest.TestCase):
    def test_heunet_running_example(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log = xes_importer.import_log(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        heu_net = heuristics_miner.apply_heu(log)
        gviz = hn_vis.apply(heu_net)
        del gviz

    def test_petrinet_running_example(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log = xes_importer.import_log(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        net, im, fm = heuristics_miner.apply(log)
        gviz = pn_vis.apply(net, im, fm)
        del gviz

    def test_petrinet_receipt_df(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        df = csv_import_adapter.import_dataframe_from_path(os.path.join(INPUT_DATA_DIR, "running-example.csv"))
        net, im, fm = heuristics_miner.apply(df)
        gviz = pn_vis.apply(net, im, fm)
        del gviz

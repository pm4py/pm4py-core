import os
import unittest

from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.visualization.heuristics_net import visualizer as hn_vis
from pm4py.visualization.petri_net import visualizer as pn_vis
from pm4py.util import constants, pandas_utils
from tests.constants import INPUT_DATA_DIR


class HeuMinerTest(unittest.TestCase):
    def test_heunet_running_example(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log = xes_importer.apply(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        heu_net = heuristics_miner.apply_heu(log)
        gviz = hn_vis.apply(heu_net)
        del gviz

    def test_petrinet_running_example(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log = xes_importer.apply(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        net, im, fm = heuristics_miner.apply(log)
        gviz = pn_vis.apply(net, im, fm)
        del gviz

    def test_petrinet_receipt_df(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        df = pandas_utils.read_csv(os.path.join(INPUT_DATA_DIR, "receipt.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        net, im, fm = heuristics_miner.apply(df)
        gviz = pn_vis.apply(net, im, fm)
        del gviz

    def test_heuplusplus_perf_df(self):
        df = pandas_utils.read_csv(os.path.join(INPUT_DATA_DIR, "interval_event_log.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        heu_net = heuristics_miner.Variants.PLUSPLUS.value.apply_heu_pandas(df, parameters={"heu_net_decoration": "performance"})
        gviz = hn_vis.apply(heu_net)

    def test_heuplusplus_perf_log(self):
        log = xes_importer.apply(os.path.join(INPUT_DATA_DIR, "interval_event_log.xes"))
        heu_net = heuristics_miner.apply_heu(log, variant=heuristics_miner.Variants.PLUSPLUS, parameters={"heu_net_decoration": "performance"})
        gviz = hn_vis.apply(heu_net)

    def test_heuplusplus_petri_df(self):
        df = pandas_utils.read_csv(os.path.join(INPUT_DATA_DIR, "interval_event_log.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        net, im, fm = heuristics_miner.Variants.PLUSPLUS.value.apply_pandas(df)
        gviz = pn_vis.apply(net, im, fm)

    def test_heuplusplus_petri_log(self):
        log = xes_importer.apply(os.path.join(INPUT_DATA_DIR, "interval_event_log.xes"))
        net, im, fm = heuristics_miner.apply(log, variant=heuristics_miner.Variants.PLUSPLUS)
        gviz = pn_vis.apply(net, im, fm)


if __name__ == "__main__":
    unittest.main()

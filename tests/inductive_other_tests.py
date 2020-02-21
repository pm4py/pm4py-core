import unittest
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.log.importer.csv import factory as csv_importer
from pm4py.algo.discovery.inductive import factory as inductive_miner
from pm4py.statistics.variants.log import get as log_variants
from pm4py.statistics.variants.pandas import get as pd_variants
import os


class InductiveMinerOtherTests(unittest.TestCase):
    def test_dataframe_dfg_based(self):
        df = csv_importer.import_dataframe_from_path(os.path.join("input_data", "running-example.csv"))
        net, im, fm = inductive_miner.apply(df, variant=inductive_miner.DFG_BASED)


    def test_dataframe_dfg_based_old(self):
        df = csv_importer.import_dataframe_from_path(os.path.join("input_data", "running-example.csv"))
        net, im, fm = inductive_miner.apply(df, variant=inductive_miner.DFG_BASED_OLD_VERSION)


    def test_log_variants_dfg_based(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        net, im, fm = inductive_miner.apply_variants(log_variants.get_variants(log),
                                                     variant=inductive_miner.DFG_BASED)


    def test_log_tree_variants_dfg_based(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        tree = inductive_miner.apply_tree_variants(log_variants.get_variants(log),
                                                   variant=inductive_miner.DFG_BASED)


    def test_df_variants_dfg_based(self):
        df = csv_importer.import_dataframe_from_path(os.path.join("input_data", "running-example.csv"))
        net, im, fm = inductive_miner.apply_variants(pd_variants.get_variants_set(df),
                                                     variant=inductive_miner.DFG_BASED)


    def test_df_tree_variants_dfg_based(self):
        df = csv_importer.import_dataframe_from_path(os.path.join("input_data", "running-example.csv"))
        tree = inductive_miner.apply_tree_variants(pd_variants.get_variants_set(df),
                                                   variant=inductive_miner.DFG_BASED)


    def test_log_variants_dfg_based_old(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        net, im, fm = inductive_miner.apply_variants(log_variants.get_variants(log),
                                                     variant=inductive_miner.DFG_BASED_OLD_VERSION)


    def test_log_tree_variants_dfg_based_old(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        tree = inductive_miner.apply_tree_variants(log_variants.get_variants(log),
                                                   variant=inductive_miner.DFG_BASED_OLD_VERSION)


    def test_df_variants_dfg_based_old(self):
        df = csv_importer.import_dataframe_from_path(os.path.join("input_data", "running-example.csv"))
        net, im, fm = inductive_miner.apply_variants(pd_variants.get_variants_set(df),
                                                     variant=inductive_miner.DFG_BASED_OLD_VERSION)


    def test_df_tree_variants_dfg_based_old(self):
        df = csv_importer.import_dataframe_from_path(os.path.join("input_data", "running-example.csv"))
        tree = inductive_miner.apply_tree_variants(pd_variants.get_variants_set(df),
                                                   variant=inductive_miner.DFG_BASED_OLD_VERSION)


if __name__ == "__main__":
    unittest.main()

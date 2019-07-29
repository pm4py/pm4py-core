import os
import unittest

from pm4py.algo.filtering.pandas.ltl import ltl_checker
from pm4py.objects.log.adapters.pandas import csv_import_adapter


class LtlCheckingPandasTest(unittest.TestCase):
    def test_AeventuallyB_pos(self):
        df = csv_import_adapter.import_dataframe_from_path(os.path.join("input_data", "running-example.csv"))
        filt_A_ev_B_pos = ltl_checker.A_eventually_B(df, "check ticket", "pay compensation",
                                                     parameters={"positive": True})

    def test_AeventuallyB_neg(self):
        df = csv_import_adapter.import_dataframe_from_path(os.path.join("input_data", "running-example.csv"))
        filt_A_ev_B_neg = ltl_checker.A_eventually_B(df, "check ticket", "pay compensation",
                                                     parameters={"positive": False})

    def test_AeventuallyBeventuallyC_pos(self):
        df = csv_import_adapter.import_dataframe_from_path(os.path.join("input_data", "running-example.csv"))
        filt_A_ev_B_ev_C_pos = ltl_checker.A_eventually_B_eventually_C(df, "check ticket", "decide",
                                                                       "pay compensation",
                                                                       parameters={"positive": True})

    def test_AeventuallyBeventuallyC_neg(self):
        df = csv_import_adapter.import_dataframe_from_path(os.path.join("input_data", "running-example.csv"))
        filt_A_ev_B_ev_C_neg = ltl_checker.A_eventually_B_eventually_C(df, "check ticket", "decide",
                                                                       "pay compensation",
                                                                       parameters={"positive": False})

    def test_AnextBnextC_pos(self):
        df = csv_import_adapter.import_dataframe_from_path(os.path.join("input_data", "running-example.csv"))
        filt_A_next_B_next_C_pos = ltl_checker.A_next_B_next_C(df, "check ticket", "decide", "pay compensation",
                                                               parameters={"positive": True})

    def test_AnextBnextC_neg(self):
        df = csv_import_adapter.import_dataframe_from_path(os.path.join("input_data", "running-example.csv"))
        filt_A_next_B_next_C_neg = ltl_checker.A_next_B_next_C(df, "check ticket", "decide", "pay compensation",
                                                               parameters={"positive": False})

    def test_fourEeyesPrinciple_pos(self):
        df = csv_import_adapter.import_dataframe_from_path(os.path.join("input_data", "running-example.csv"))
        filt_foureyes_pos = ltl_checker.four_eyes_principle(df, "check ticket", "pay compensation",
                                                            parameters={"positive": True})

    def test_fourEeyesPrinciple_neg(self):
        df = csv_import_adapter.import_dataframe_from_path(os.path.join("input_data", "running-example.csv"))
        filt_foureyes_neg = ltl_checker.four_eyes_principle(df, "check ticket", "pay compensation",
                                                            parameters={"positive": False})

    def test_attrValueDifferentPersons_pos(self):
        df = csv_import_adapter.import_dataframe_from_path(os.path.join("input_data", "running-example.csv"))
        attr_value_different_persons_pos = ltl_checker.attr_value_different_persons(df, "check ticket",
                                                                                    parameters={"positive": True})

    def test_attrValueDifferentPersons_neg(self):
        df = csv_import_adapter.import_dataframe_from_path(os.path.join("input_data", "running-example.csv"))
        attr_value_different_persons_neg = ltl_checker.attr_value_different_persons(df, "check ticket",
                                                                                    parameters={"positive": False})


if __name__ == "__main__":
    unittest.main()

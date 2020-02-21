import os
import unittest

from pm4py.algo.filtering.pandas.attributes import attributes_filter
from pm4py.algo.filtering.pandas.auto_filter import auto_filter
from pm4py.algo.filtering.pandas.cases import case_filter
from pm4py.algo.filtering.pandas.paths import paths_filter
from pm4py.algo.filtering.pandas.timestamp import timestamp_filter
from pm4py.algo.filtering.pandas.variants import variants_filter
from pm4py.objects.log.adapters.pandas import csv_import_adapter as csv_import_adapter
from pm4py.objects.conversion.log import factory as log_conv_fact
from pm4py.statistics.traces.pandas import case_statistics
from pm4py.algo.filtering.pandas.ltl import ltl_checker
from tests.constants import INPUT_DATA_DIR


class DataframePrefilteringTest(unittest.TestCase):
    def test_prefiltering_dataframe(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        input_log = os.path.join(INPUT_DATA_DIR, "running-example.csv")
        dataframe = csv_import_adapter.import_dataframe_from_path_wo_timeconversion(input_log, sep=',')
        dataframe = attributes_filter.filter_df_keeping_spno_activities(dataframe, activity_key="concept:name")
        dataframe = case_filter.filter_on_ncases(dataframe, case_id_glue="case:concept:name")
        dataframe = csv_import_adapter.convert_timestamp_columns_in_df(dataframe)
        dataframe = dataframe.sort_values('time:timestamp')
        event_log = log_conv_fact.apply(dataframe, variant=log_conv_fact.TO_EVENT_STREAM)
        log = log_conv_fact.apply(event_log)
        del log

    def test_autofiltering_dataframe(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        input_log = os.path.join(INPUT_DATA_DIR, "running-example.csv")
        dataframe = csv_import_adapter.import_dataframe_from_path_wo_timeconversion(input_log, sep=',')
        dataframe = auto_filter.apply_auto_filter(dataframe)
        del dataframe

    def test_filtering_variants(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        input_log = os.path.join(INPUT_DATA_DIR, "running-example.csv")
        dataframe = csv_import_adapter.import_dataframe_from_path_wo_timeconversion(input_log, sep=',')
        variants = case_statistics.get_variant_statistics(dataframe)
        chosen_variants = [variants[0]["variant"]]
        dataframe = variants_filter.apply(dataframe, chosen_variants)
        del dataframe

    def test_filtering_attr_events(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        input_log = os.path.join(INPUT_DATA_DIR, "running-example.csv")
        dataframe = csv_import_adapter.import_dataframe_from_path_wo_timeconversion(input_log, sep=',')
        df1 = attributes_filter.apply_events(dataframe, ["reject request"], parameters={"positive": True})
        df2 = attributes_filter.apply_events(dataframe, ["reject request"], parameters={"positive": False})
        del df1
        del df2

    def test_filtering_paths(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        input_log = os.path.join(INPUT_DATA_DIR, "running-example.csv")
        dataframe = csv_import_adapter.import_dataframe_from_path(input_log, sep=',')
        df3 = paths_filter.apply(dataframe, [("examine casually", "check ticket")], {"positive": False})
        del df3
        df3 = paths_filter.apply(dataframe, [("examine casually", "check ticket")], {"positive": True})
        del df3

    def test_filtering_timeframe(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        input_log = os.path.join(INPUT_DATA_DIR, "receipt.csv")
        df = csv_import_adapter.import_dataframe_from_path(input_log, sep=',')
        df1 = timestamp_filter.apply_events(df, "2011-03-09 00:00:00", "2012-01-18 23:59:59")
        df2 = timestamp_filter.filter_traces_intersecting(df, "2011-03-09 00:00:00", "2012-01-18 23:59:59")
        df3 = timestamp_filter.filter_traces_contained(df, "2011-03-09 00:00:00", "2012-01-18 23:59:59")
        del df1
        del df2
        del df3

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

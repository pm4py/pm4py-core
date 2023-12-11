import os
import unittest

from pm4py.algo.filtering.pandas.attributes import attributes_filter
from pm4py.algo.filtering.pandas.cases import case_filter
from pm4py.algo.filtering.pandas.paths import paths_filter
from pm4py.algo.filtering.pandas.timestamp import timestamp_filter
from pm4py.algo.filtering.pandas.variants import variants_filter
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.conversion.log import converter as log_conv_fact
from pm4py.statistics.traces.generic.pandas import case_statistics
from pm4py.algo.filtering.pandas.ltl import ltl_checker
from tests.constants import INPUT_DATA_DIR
from pm4py.util import constants, pandas_utils


class DataframePrefilteringTest(unittest.TestCase):
    def test_prefiltering_dataframe(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        input_log = os.path.join(INPUT_DATA_DIR, "running-example.csv")
        dataframe = pandas_utils.read_csv(input_log)
        dataframe = dataframe_utils.convert_timestamp_columns_in_df(dataframe, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        dataframe = attributes_filter.filter_df_keeping_spno_activities(dataframe, activity_key="concept:name")
        dataframe = case_filter.filter_on_ncases(dataframe, case_id_glue="case:concept:name")
        dataframe = dataframe.sort_values('time:timestamp')
        event_log = log_conv_fact.apply(dataframe, variant=log_conv_fact.TO_EVENT_STREAM)
        log = log_conv_fact.apply(event_log, variant=log_conv_fact.Variants.TO_EVENT_LOG)
        del log

    def test_filtering_variants(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        input_log = os.path.join(INPUT_DATA_DIR, "running-example.csv")
        dataframe = pandas_utils.read_csv(input_log)
        dataframe = dataframe_utils.convert_timestamp_columns_in_df(dataframe, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        variants = case_statistics.get_variant_statistics(dataframe)
        chosen_variants = [variants[0]["variant"]]
        dataframe = variants_filter.apply(dataframe, chosen_variants)
        del dataframe

    def test_filtering_attr_events(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        input_log = os.path.join(INPUT_DATA_DIR, "running-example.csv")
        dataframe = pandas_utils.read_csv(input_log)
        dataframe = dataframe_utils.convert_timestamp_columns_in_df(dataframe, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        df1 = attributes_filter.apply_events(dataframe, ["reject request"],
                                             parameters={attributes_filter.Parameters.POSITIVE: True})
        df2 = attributes_filter.apply_events(dataframe, ["reject request"],
                                             parameters={attributes_filter.Parameters.POSITIVE: False})
        del df1
        del df2

    def test_filtering_paths(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        input_log = os.path.join(INPUT_DATA_DIR, "running-example.csv")
        dataframe = pandas_utils.read_csv(input_log)
        dataframe = dataframe_utils.convert_timestamp_columns_in_df(dataframe, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        df3 = paths_filter.apply(dataframe, [("examine casually", "check ticket")],
                                 {paths_filter.Parameters.POSITIVE: False})
        del df3
        df3 = paths_filter.apply(dataframe, [("examine casually", "check ticket")],
                                 {paths_filter.Parameters.POSITIVE: True})
        del df3

    def test_filtering_timeframe(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        input_log = os.path.join(INPUT_DATA_DIR, "receipt.csv")
        df = pandas_utils.read_csv(input_log)
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        df1 = timestamp_filter.apply_events(df, "2011-03-09 00:00:00", "2012-01-18 23:59:59")
        df2 = timestamp_filter.filter_traces_intersecting(df, "2011-03-09 00:00:00", "2012-01-18 23:59:59")
        df3 = timestamp_filter.filter_traces_contained(df, "2011-03-09 00:00:00", "2012-01-18 23:59:59")
        del df1
        del df2
        del df3

    def test_filtering_traces_attribute_in_timeframe(self):
        input_log = os.path.join(INPUT_DATA_DIR, "receipt.csv")
        df = pandas_utils.read_csv(input_log)
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        df1 = timestamp_filter.filter_traces_attribute_in_timeframe(df, "concept:name", "Confirmation of receipt", "2011-03-09 00:00:00", "2012-01-18 23:59:59")

    def test_AeventuallyB_pos(self):
        df = pandas_utils.read_csv(os.path.join("input_data", "running-example.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        filt_A_ev_B_pos = ltl_checker.eventually_follows(df, ["check ticket", "pay compensation"],
                                                     parameters={ltl_checker.Parameters.POSITIVE: True})

    def test_AeventuallyB_neg(self):
        df = pandas_utils.read_csv(os.path.join("input_data", "running-example.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        filt_A_ev_B_neg = ltl_checker.eventually_follows(df, ["check ticket", "pay compensation"],
                                                     parameters={ltl_checker.Parameters.POSITIVE: False})

    def test_AeventuallyBeventuallyC_pos(self):
        df = pandas_utils.read_csv(os.path.join("input_data", "running-example.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        filt_A_ev_B_ev_C_pos = ltl_checker.eventually_follows(df, ["check ticket", "decide",
                                                                       "pay compensation"],
                                                                       parameters={
                                                                           ltl_checker.Parameters.POSITIVE: True})

    def test_AeventuallyBeventuallyC_neg(self):
        df = pandas_utils.read_csv(os.path.join("input_data", "running-example.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        filt_A_ev_B_ev_C_neg = ltl_checker.eventually_follows(df, ["check ticket", "decide",
                                                                       "pay compensation"],
                                                                       parameters={
                                                                           ltl_checker.Parameters.POSITIVE: False})

    def test_AnextBnextC_pos(self):
        df = pandas_utils.read_csv(os.path.join("input_data", "running-example.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        filt_A_next_B_next_C_pos = ltl_checker.A_next_B_next_C(df, "check ticket", "decide", "pay compensation",
                                                               parameters={ltl_checker.Parameters.POSITIVE: True})

    def test_AnextBnextC_neg(self):
        df = pandas_utils.read_csv(os.path.join("input_data", "running-example.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        filt_A_next_B_next_C_neg = ltl_checker.A_next_B_next_C(df, "check ticket", "decide", "pay compensation",
                                                               parameters={ltl_checker.Parameters.POSITIVE: False})

    def test_fourEeyesPrinciple_pos(self):
        df = pandas_utils.read_csv(os.path.join("input_data", "running-example.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        filt_foureyes_pos = ltl_checker.four_eyes_principle(df, "check ticket", "pay compensation",
                                                            parameters={ltl_checker.Parameters.POSITIVE: True})

    def test_fourEeyesPrinciple_neg(self):
        df = pandas_utils.read_csv(os.path.join("input_data", "running-example.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        filt_foureyes_neg = ltl_checker.four_eyes_principle(df, "check ticket", "pay compensation",
                                                            parameters={ltl_checker.Parameters.POSITIVE: False})

    def test_attrValueDifferentPersons_pos(self):
        df = pandas_utils.read_csv(os.path.join("input_data", "running-example.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        attr_value_different_persons_pos = ltl_checker.attr_value_different_persons(df, "check ticket",
                                                                                    parameters={
                                                                                        ltl_checker.Parameters.POSITIVE: True})

    def test_attrValueDifferentPersons_neg(self):
        df = pandas_utils.read_csv(os.path.join("input_data", "running-example.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        attr_value_different_persons_neg = ltl_checker.attr_value_different_persons(df, "check ticket",
                                                                                    parameters={
                                                                                        ltl_checker.Parameters.POSITIVE: False})


    def test_attr_value_repetition(self):
        from pm4py.algo.filtering.pandas.attr_value_repetition import filter
        df = pandas_utils.read_csv(os.path.join("input_data", "running-example.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        filtered_df = filter.apply(df, "Sara", parameters={constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY: "org:resource"})


if __name__ == "__main__":
    unittest.main()

import os
import unittest

from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.algo.filtering.log.cases import case_filter
from pm4py.algo.filtering.log.end_activities import end_activities_filter
from pm4py.algo.filtering.log.paths import paths_filter
from pm4py.algo.filtering.log.start_activities import start_activities_filter
from pm4py.algo.filtering.log.variants import variants_filter as variants_module
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.statistics.traces.generic.log import case_statistics
from pm4py.algo.filtering.log.ltl import ltl_checker
from pm4py.algo.filtering.log.timestamp import timestamp_filter
from tests.constants import INPUT_DATA_DIR
from pm4py.util import constants, pandas_utils


class LogFilteringTest(unittest.TestCase):
    def test_filtering_attributes_events(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        input_log = os.path.join(INPUT_DATA_DIR, "running-example.xes")
        log = xes_importer.apply(input_log)
        log1 = attributes_filter.apply_events(log, ["reject request"],
                                              parameters={attributes_filter.Parameters.POSITIVE: True})
        log2 = attributes_filter.apply_events(log, ["reject request"],
                                              parameters={attributes_filter.Parameters.POSITIVE: True})
        del log1
        del log2

    def test_filtering_attributes_traces(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        input_log = os.path.join(INPUT_DATA_DIR, "running-example.xes")
        log = xes_importer.apply(input_log)
        log1 = attributes_filter.apply(log, ["reject request"],
                                       parameters={attributes_filter.Parameters.POSITIVE: True})
        log2 = attributes_filter.apply(log, ["reject request"],
                                       parameters={attributes_filter.Parameters.POSITIVE: True})
        del log1
        del log2

    def test_attribute_selection(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        input_log = os.path.join(INPUT_DATA_DIR, "running-example.xes")
        log = xes_importer.apply(input_log)
        attributes_filter.select_attributes_from_log_for_tree(log)

    def test_filtering_variants(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        input_log = os.path.join(INPUT_DATA_DIR, "running-example.xes")
        log = xes_importer.apply(input_log)
        considered_variant = "register request,examine casually,check ticket,decide,reinitiate request"
        considered_variant = considered_variant + ",examine thoroughly,check ticket,decide,pay compensation"
        log1 = variants_module.apply(log, [
            considered_variant],
                                     parameters={attributes_filter.Parameters.POSITIVE: False})
        log2 = variants_module.apply(log, [
            considered_variant],
                                     parameters={attributes_filter.Parameters.POSITIVE: True})
        del log1
        del log2

    def test_obtaining_variants(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        input_log = os.path.join(INPUT_DATA_DIR, "running-example.xes")
        log = xes_importer.apply(input_log)
        stats = case_statistics.get_variant_statistics(log)
        del stats

    def test_casefilter_ncases(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        input_log = os.path.join(INPUT_DATA_DIR, "running-example.xes")
        log = xes_importer.apply(input_log)
        cases = case_filter.filter_on_ncases(log, 1)
        del cases

    def test_casefilter_casesize(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        input_log = os.path.join(INPUT_DATA_DIR, "running-example.xes")
        log = xes_importer.apply(input_log)
        cases = case_filter.filter_on_case_size(log, min_case_size=3, max_case_size=5)
        del cases

    def test_pathsfilter(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        input_log = os.path.join(INPUT_DATA_DIR, "running-example.xes")
        log = xes_importer.apply(input_log)
        log1 = paths_filter.apply(log, [("examine casually", "check ticket")], {paths_filter.Parameters.POSITIVE: True})
        log2 = paths_filter.apply(log, [("examine casually", "check ticket")], {paths_filter.Parameters.POSITIVE: False})
        del log1
        del log2

    def test_AeventuallyB_pos(self):
        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
        filt_A_ev_B_pos = ltl_checker.eventually_follows(log, ["check ticket", "pay compensation"],
                                                     parameters={ltl_checker.Parameters.POSITIVE: True})

    def test_AeventuallyB_neg(self):
        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
        filt_A_ev_B_neg = ltl_checker.eventually_follows(log, ["check ticket", "pay compensation"],
                                                     parameters={ltl_checker.Parameters.POSITIVE: False})

    def test_AeventuallyBeventuallyC_pos(self):
        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
        filt_A_ev_B_ev_C_pos = ltl_checker.eventually_follows(log, ["check ticket", "decide",
                                                                       "pay compensation"],
                                                                       parameters={
                                                                           ltl_checker.Parameters.POSITIVE: True})

    def test_AeventuallyBeventuallyC_neg(self):
        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
        filt_A_ev_B_ev_C_neg = ltl_checker.eventually_follows(log, ["check ticket", "decide",
                                                                       "pay compensation"],
                                                                       parameters={
                                                                           ltl_checker.Parameters.POSITIVE: False})

    def test_AnextBnextC_pos(self):
        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
        filt_A_next_B_next_C_pos = ltl_checker.A_next_B_next_C(log, "check ticket", "decide", "pay compensation",
                                                               parameters={ltl_checker.Parameters.POSITIVE: True})

    def test_AnextBnextC_neg(self):
        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
        filt_A_next_B_next_C_neg = ltl_checker.A_next_B_next_C(log, "check ticket", "decide", "pay compensation",
                                                               parameters={ltl_checker.Parameters.POSITIVE: False})

    def test_fourEeyesPrinciple_pos(self):
        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
        filt_foureyes_pos = ltl_checker.four_eyes_principle(log, "check ticket", "pay compensation",
                                                            parameters={ltl_checker.Parameters.POSITIVE: True})

    def test_fourEeyesPrinciple_neg(self):
        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
        filt_foureyes_neg = ltl_checker.four_eyes_principle(log, "check ticket", "pay compensation",
                                                            parameters={ltl_checker.Parameters.POSITIVE: False})

    def test_attrValueDifferentPersons_pos(self):
        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
        attr_value_different_persons_pos = ltl_checker.attr_value_different_persons(log, "check ticket",
                                                                                    parameters={
                                                                                        ltl_checker.Parameters.POSITIVE: True})

    def test_attrValueDifferentPersons_neg(self):
        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
        attr_value_different_persons_neg = ltl_checker.attr_value_different_persons(log, "check ticket",
                                                                                    parameters={
                                                                                        ltl_checker.Parameters.POSITIVE: False})


    def test_attr_value_repetition(self):
        from pm4py.algo.filtering.log.attr_value_repetition import filter
        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
        filtered_log = filter.apply(log, "Sara", parameters={constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY: "org:resource"})

    def test_filter_traces_attribute_in_timeframe(self):
        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
        filtered_log = timestamp_filter.filter_traces_attribute_in_timeframe(log, "concept:name", "reinitiate request", "2011-01-06 00:00:00", "2011-01-07 23:59:59")


if __name__ == "__main__":
    unittest.main()

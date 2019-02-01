import os
import unittest

from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.algo.filtering.log.cases import case_filter
from pm4py.algo.filtering.log.end_activities import end_activities_filter
from pm4py.algo.filtering.log.paths import paths_filter
from pm4py.algo.filtering.log.start_activities import start_activities_filter
from pm4py.algo.filtering.log.variants import variants_filter as variants_module
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.statistics.traces.log import case_statistics
from tests.constants import INPUT_DATA_DIR


class LogFilteringTest(unittest.TestCase):
    def test_logfiltering_filtering1(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        input_log = os.path.join(INPUT_DATA_DIR, "running-example.xes")
        log = xes_importer.import_log(input_log)
        log = attributes_filter.apply_auto_filter(log)
        log = variants_module.apply_auto_filter(log)
        log = start_activities_filter.apply_auto_filter(log)
        log = end_activities_filter.apply_auto_filter(log)
        log = paths_filter.apply_auto_filter(log)
        del log

    def test_filtering_attributes_events(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        input_log = os.path.join(INPUT_DATA_DIR, "running-example.xes")
        log = xes_importer.import_log(input_log)
        log1 = attributes_filter.apply_events(log, ["reject request"], parameters={"positive": True})
        log2 = attributes_filter.apply_events(log, ["reject request"], parameters={"positive": True})
        del log1
        del log2

    def test_filtering_attributes_traces(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        input_log = os.path.join(INPUT_DATA_DIR, "running-example.xes")
        log = xes_importer.import_log(input_log)
        log1 = attributes_filter.apply(log, ["reject request"], parameters={"positive": True})
        log2 = attributes_filter.apply(log, ["reject request"], parameters={"positive": True})
        del log1
        del log2

    def test_attribute_selection(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        input_log = os.path.join(INPUT_DATA_DIR, "running-example.xes")
        log = xes_importer.import_log(input_log)
        attributes_filter.select_attributes_from_log_for_tree(log)

    def test_filtering_variants(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        input_log = os.path.join(INPUT_DATA_DIR, "running-example.xes")
        log = xes_importer.import_log(input_log)
        considered_variant = "register request,examine casually,check ticket,decide,reinitiate request"
        considered_variant = considered_variant + ",examine thoroughly,check ticket,decide,pay compensation"
        log1 = variants_module.apply(log, [
            considered_variant],
                                     parameters={"positive": False})
        log2 = variants_module.apply(log, [
            considered_variant],
                                     parameters={"positive": True})
        del log1
        del log2

    def test_obtaining_variants(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        input_log = os.path.join(INPUT_DATA_DIR, "running-example.xes")
        log = xes_importer.import_log(input_log)
        stats = case_statistics.get_variant_statistics(log)
        del stats

    def test_casefilter_ncases(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        input_log = os.path.join(INPUT_DATA_DIR, "running-example.xes")
        log = xes_importer.import_log(input_log)
        cases = case_filter.filter_on_ncases(log, 1)
        del cases

    def test_casefilter_casesize(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        input_log = os.path.join(INPUT_DATA_DIR, "running-example.xes")
        log = xes_importer.import_log(input_log)
        cases = case_filter.filter_on_case_size(log, min_case_size=3, max_case_size=5)
        del cases

    def test_pathsfilter(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        input_log = os.path.join(INPUT_DATA_DIR, "running-example.xes")
        log = xes_importer.import_log(input_log)
        log1 = paths_filter.apply(log, [("examine casually", "check ticket")], {"positive": True})
        log2 = paths_filter.apply(log, [("examine casually", "check ticket")], {"positive": False})
        del log1
        del log2


if __name__ == "__main__":
    unittest.main()

import unittest
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from tests.constants import INPUT_DATA_DIR
from pm4py.entities.log.importer.xes import factory as xes_importer
from pm4py.algo.filtering.tracelog.paths import paths_filter
from pm4py.algo.filtering.tracelog.start_activities import start_activities_filter
from pm4py.algo.filtering.tracelog.attributes import attributes_filter
from pm4py.algo.filtering.tracelog.end_activities import end_activities_filter
from pm4py.algo.filtering.tracelog.cases import case_filter
from pm4py.algo.filtering.tracelog.variants import variants_filter as variants_module
from pm4py.algo.cases.tracelog import case_statistics

class LogFilteringTest(unittest.TestCase):
    def test_logfiltering_filtering1(self):
        inputLog = os.path.join(INPUT_DATA_DIR, "running-example.xes")
        log = xes_importer.import_log(inputLog)
        log = attributes_filter.apply_auto_filter(log)
        log = variants_module.apply_auto_filter(log)
        log = start_activities_filter.apply_auto_filter(log)
        log = end_activities_filter.apply_auto_filter(log)
        log = paths_filter.apply_auto_filter(log)

    def test_filtering_attributes_events(self):
        inputLog = os.path.join(INPUT_DATA_DIR, "running-example.xes")
        log = xes_importer.import_log(inputLog)
        log1 = attributes_filter.apply_events(log, ["reject request"], parameters={"positive": True})
        log2 = attributes_filter.apply_events(log, ["reject request"], parameters={"positive": True})

    def test_filtering_attributes_traces(self):
        inputLog = os.path.join(INPUT_DATA_DIR, "running-example.xes")
        log = xes_importer.import_log(inputLog)
        log1 = attributes_filter.apply(log, ["reject request"], parameters={"positive": True})
        log2 = attributes_filter.apply(log, ["reject request"], parameters={"positive": True})

    def test_filtering_variants(self):
        inputLog = os.path.join(INPUT_DATA_DIR, "running-example.xes")
        log = xes_importer.import_log(inputLog)
        log1 = variants_module.apply(log, ["register request,examine casually,check ticket,decide,reinitiate request,examine thoroughly,check ticket,decide,pay compensation"], parameters={"positive":False})
        log2 = variants_module.apply(log, ["register request,examine casually,check ticket,decide,reinitiate request,examine thoroughly,check ticket,decide,pay compensation"], parameters={"positive":True})

    def test_obtaining_variants(self):
        inputLog = os.path.join(INPUT_DATA_DIR, "running-example.xes")
        log = xes_importer.import_log(inputLog)
        stats = case_statistics.get_variant_statistics(log)

    def test_casefilter_ncases(self):
        inputLog = os.path.join(INPUT_DATA_DIR, "running-example.xes")
        log = xes_importer.import_log(inputLog)
        cases = case_filter.filter_on_ncases(log, 1)

    def test_casefilter_casesize(self):
        inputLog = os.path.join(INPUT_DATA_DIR, "running-example.xes")
        log = xes_importer.import_log(inputLog)
        cases = case_filter.filter_on_case_size(log, min_case_size=3, max_case_size=5)

    def test_pathsfilter(self):
        inputLog = os.path.join(INPUT_DATA_DIR, "running-example.xes")
        log = xes_importer.import_log(inputLog)
        log1 = paths_filter.apply(log, [("examine casually", "check ticket")], {"positive": True})
        log2 = paths_filter.apply(log, [("examine casually", "check ticket")], {"positive": False})

if __name__ == "__main__":
    unittest.main()
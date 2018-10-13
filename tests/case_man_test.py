import unittest
import os, sys, inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.statistics.traces.tracelog import case_statistics as case_statistics_log
from pm4py.statistics.traces.pandas import case_statistics as case_statistics_pd
from pm4py.objects.log.importer.csv.versions import pandas_df_imp


class CaseManagementTest(unittest.TestCase):
    def test_casemanagementlogs(self):
        log_path = os.path.join("input_data", "running-example.xes")
        log = xes_importer.import_log(log_path)
        cases = case_statistics_log.get_cases_description(log)

    def test_casemanagement(self):
        log_path = os.path.join("input_data", "running-example.csv")
        df = pandas_df_imp.import_dataframe_from_path(log_path)
        cases = case_statistics_pd.get_cases_description(df)

    def test_eventretrieval_pandas(self):
        log_path = os.path.join("input_data", "running-example.csv")
        df = pandas_df_imp.import_dataframe_from_path(log_path)
        events = case_statistics_pd.get_events(df, 1)

    def test_eventretrieval_log(self):
        log_path = os.path.join("input_data", "running-example.xes")
        log = xes_importer.import_log(log_path)
        events = case_statistics_log.get_events(log, "1")


if __name__ == "__main__":
    unittest.main()

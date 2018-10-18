import os
import unittest

from pm4py.objects.log.importer.csv.versions import pandas_df_imp
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.statistics.traces.pandas import case_statistics as case_statistics_pd
from pm4py.statistics.traces.tracelog import case_statistics as case_statistics_log


class CaseManagementTest(unittest.TestCase):
    def test_casemanagementlogs(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log_path = os.path.join("input_data", "running-example.xes")
        log = xes_importer.import_log(log_path)
        cases = case_statistics_log.get_cases_description(log)
        del cases

    def test_casemanagement(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log_path = os.path.join("input_data", "running-example.csv")
        df = pandas_df_imp.import_dataframe_from_path(log_path)
        cases = case_statistics_pd.get_cases_description(df)
        del cases

    def test_eventretrieval_pandas(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log_path = os.path.join("input_data", "running-example.csv")
        df = pandas_df_imp.import_dataframe_from_path(log_path)
        events = case_statistics_pd.get_events(df, 1)
        del events

    def test_eventretrieval_log(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log_path = os.path.join("input_data", "running-example.xes")
        log = xes_importer.import_log(log_path)
        events = case_statistics_log.get_events(log, "1")
        del events


if __name__ == "__main__":
    unittest.main()

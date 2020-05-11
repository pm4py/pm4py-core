import os
import unittest

from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.log.adapters.pandas import csv_import_adapter
from pm4py.statistics.passed_time.log import factory as log_passed_time
from pm4py.statistics.passed_time.pandas import factory as df_passed_time

class PassedTimeTest(unittest.TestCase):
    def test_passedtime_prepost_log(self):
        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
        prepost = log_passed_time.apply(log, "decide", variant="prepost")
        del prepost

    def test_passedtime_prepost_df(self):
        df = csv_import_adapter.import_dataframe_from_path(os.path.join("input_data", "running-example.csv"))
        prepost = df_passed_time.apply(df, "decide", variant="prepost")
        del prepost

if __name__ == "__main__":
    unittest.main()

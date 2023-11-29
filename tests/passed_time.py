import os
import unittest

from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.util import dataframe_utils
from pm4py.util import constants, pandas_utils
from pm4py.statistics.passed_time.log import algorithm as log_passed_time
from pm4py.statistics.passed_time.pandas import algorithm as df_passed_time


class PassedTimeTest(unittest.TestCase):
    def test_passedtime_prepost_log(self):
        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
        prepost = log_passed_time.apply(log, "decide", variant=log_passed_time.Variants.PREPOST)
        del prepost

    def test_passedtime_prepost_df(self):
        df = pandas_utils.read_csv(os.path.join("input_data", "running-example.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        prepost = df_passed_time.apply(df, "decide", variant=df_passed_time.Variants.PREPOST)
        del prepost


if __name__ == "__main__":
    unittest.main()

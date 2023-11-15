import unittest
import os

from pm4py.objects.log.importer.xes import importer as xes_importer
import pandas as pd
from pm4py.objects.log.util import dataframe_utils
from pm4py.util import constants
from pm4py.algo.organizational_mining.roles import algorithm as role_mining


class RoleDetectionTest(unittest.TestCase):
    def test_role_running_csv(self):
        df = pd.read_csv(os.path.join("input_data", "running-example.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format="ISO8601")
        roles = role_mining.apply(df)

    def test_role_running_xes(self):
        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
        roles = role_mining.apply(log)

    def test_role_receipt_csv(self):
        df = pd.read_csv(os.path.join("input_data", "receipt.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format="ISO8601")
        roles = role_mining.apply(df)

    def test_role_receipt_xes(self):
        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "receipt.xes"))
        roles = role_mining.apply(log)


if __name__ == "__main__":
    unittest.main()

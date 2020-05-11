import unittest
import os

from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.log.adapters.pandas import csv_import_adapter
from pm4py.algo.enhancement.roles import factory as role_mining_factory


class RoleDetectionTest(unittest.TestCase):
    def test_role_running_csv(self):
        df = csv_import_adapter.import_dataframe_from_path(os.path.join("input_data", "running-example.csv"))
        roles = role_mining_factory.apply(df)

    def test_role_running_xes(self):
        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
        roles = role_mining_factory.apply(log)

    def test_role_receipt_csv(self):
        df = csv_import_adapter.import_dataframe_from_path(os.path.join("input_data", "receipt.csv"))
        roles = role_mining_factory.apply(df)

    def test_role_receipt_xes(self):
        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "receipt.xes"))
        roles = role_mining_factory.apply(log)


if __name__ == "__main__":
    unittest.main()

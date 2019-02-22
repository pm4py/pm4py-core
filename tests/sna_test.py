import os
import unittest

from pm4py.algo.enhancement.sna import factory as sna_factory
from pm4py.objects.log.adapters.pandas import csv_import_adapter
from pm4py.objects.log.importer.xes import factory as xes_importer


class SnaTests(unittest.TestCase):
    def test_1(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"

        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))

        hw_values = sna_factory.apply(log, variant="handover")
        wt_values = sna_factory.apply(log, variant="working_together")
        sub_values = sna_factory.apply(log, variant="subcontracting")
        ja_values = sna_factory.apply(log, variant="jointactivities")

    def test_pandas(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"

        log = csv_import_adapter.import_dataframe_from_path(os.path.join("..", "tests", "input_data", "running-example.csv"))

        hw_values = sna_factory.apply(log, variant="handover")
        wt_values = sna_factory.apply(log, variant="working_together")
        sub_values = sna_factory.apply(log, variant="subcontracting")

if __name__ == "__main__":
    unittest.main()

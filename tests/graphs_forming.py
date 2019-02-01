import os
import unittest

from pm4py.objects.log.adapters.pandas import csv_import_adapter
from pm4py.statistics.traces.pandas import case_statistics as pd_case_statistics
from pm4py.visualization.graphs import factory as graphs_factory
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.statistics.traces.log import case_statistics as log_case_statistics
from pm4py.algo.filtering.log.attributes import attributes_filter as log_attributes_filter
from pm4py.algo.filtering.pandas.attributes import attributes_filter as pd_attributes_filter


class GraphsForming(unittest.TestCase):
    def test_dfCasedurationPlotSemilogx(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"

        df = csv_import_adapter.import_dataframe_from_path(os.path.join("input_data", "receipt.csv"))
        x, y = pd_case_statistics.get_kde_caseduration(df)
        json = pd_case_statistics.get_kde_caseduration_json(df)
        del json

    def test_logCaseDurationPlotSemiLogx(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"

        log = xes_importer.apply(os.path.join("input_data", "receipt.xes"))
        x, y = log_case_statistics.get_kde_caseduration(log)
        json = log_case_statistics.get_kde_caseduration_json(log)
        del json

    def test_dfNumericAttribute(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"

        df = csv_import_adapter.import_dataframe_from_path(os.path.join("input_data", "roadtraffic100traces.csv"))
        x, y = pd_attributes_filter.get_kde_numeric_attribute(df, "amount")
        json = pd_attributes_filter.get_kde_numeric_attribute_json(df, "amount")
        del json

    def test_logNumericAttribute(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"

        log = xes_importer.apply(os.path.join("input_data", "roadtraffic100traces.xes"))
        x, y = log_attributes_filter.get_kde_numeric_attribute(log, "amount")
        json = log_attributes_filter.get_kde_numeric_attribute_json(log, "amount")
        del json

    def test_dfDateAttribute(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"

        df = csv_import_adapter.import_dataframe_from_path(os.path.join("input_data", "receipt.csv"))
        x, y = pd_attributes_filter.get_kde_date_attribute(df)
        json = pd_attributes_filter.get_kde_date_attribute_json(df)
        del json

    def test_logDateAttribute(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"

        log = xes_importer.apply(os.path.join("input_data", "receipt.xes"))
        x, y = log_attributes_filter.get_kde_date_attribute(log)
        json = log_attributes_filter.get_kde_date_attribute_json(log)
        del json


if __name__ == "__main__":
    unittest.main()

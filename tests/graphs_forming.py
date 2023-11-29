import os
import unittest

from pm4py.statistics.traces.generic.pandas import case_statistics as pd_case_statistics
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.statistics.traces.generic.log import case_statistics as log_case_statistics
from pm4py.statistics.attributes.log import get as log_attributes_filter
from pm4py.statistics.attributes.pandas import get as pd_attributes_filter
from pm4py.util import constants, pandas_utils
from pm4py.objects.log.util import dataframe_utils


class GraphsForming(unittest.TestCase):
    def test_dfCasedurationPlotSemilogx(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"

        df = pandas_utils.read_csv(os.path.join("input_data", "receipt.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
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

        df = pandas_utils.read_csv(os.path.join("input_data", "roadtraffic100traces.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)

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


if __name__ == "__main__":
    unittest.main()

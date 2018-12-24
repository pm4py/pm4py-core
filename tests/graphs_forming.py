import os
import unittest

from pm4py.objects.log.adapters.pandas import csv_import_adapter
from pm4py.statistics.traces.pandas import case_statistics as pd_case_statistics
from pm4py.visualization.graphs import factory as graphs_factory
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.statistics.traces.tracelog import case_statistics as log_case_statistics


class GraphsForming(unittest.TestCase):
    def test_dfCasedurationPlotSemilogx(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"

        df = csv_import_adapter.import_dataframe_from_path(os.path.join("input_data", "receipt.csv"))
        x, y = pd_case_statistics.get_kde_caseduration(df)
        json = pd_case_statistics.get_kde_caseduration_json(df)
        del json
        graph = graphs_factory.apply_plot(x, y, variant="cases", parameters={"format": "svg"})
        del graph
        graph = graphs_factory.apply_semilogx(x, y, variant="cases", parameters={"format": "svg"})
        del graph

    def test_logCaseDurationPlotSemiLogx(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"

        log = xes_importer.apply(os.path.join("input_data", "receipt.xes"))
        x, y = log_case_statistics.get_kde_caseduration(log)
        json = log_case_statistics.get_kde_caseduration_json(log)
        del json
        graph = graphs_factory.apply_plot(x, y, variant="cases", parameters={"format": "svg"})
        del graph
        graph = graphs_factory.apply_semilogx(x, y, variant="cases", parameters={"format": "svg"})
        del graph



if __name__ == "__main__":
    unittest.main()

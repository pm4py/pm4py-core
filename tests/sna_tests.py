import os
import unittest

from pm4py.algo.enhancement.sna.metrics.handover import factory as handover_of_work
from pm4py.algo.enhancement.sna.metrics.real_handover import factory as real_handover_of_work
from pm4py.algo.enhancement.sna.metrics.similar_activities import factory as similar_activities
from pm4py.algo.enhancement.sna.transformer.pandas import factory as sna_transformer_df
from pm4py.algo.enhancement.sna.transformer.tracelog import factory as sna_transformer
from pm4py.objects.log.adapters.pandas import csv_import_adapter
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.visualization.sna import factory as sna_vis_factory


class SnaTests(unittest.TestCase):
    def test_sna_df(self):
        # loads the dataframe from the CSV file
        csv_path = os.path.join("..", "tests", "input_data", "running-example.csv")
        df = csv_import_adapter.import_dataframe_from_path_wo_timeconversion(csv_path)
        # calculates the Matrix Container object
        mco = sna_transformer_df.apply(df)
        # calculates the Handover of Work matrix
        hw_matrix = handover_of_work.apply(mco)
        # calculates the Similar Activities matrix
        sim_act_matrix = similar_activities.apply(mco)
        # calculates the Real Handover of Work matrix
        real_hw_matrix = real_handover_of_work.apply(mco)

    def test_sna_log(self):
        # loads the log from XES file
        log_path = os.path.join("..", "tests", "input_data", "receipt.xes")
        log = xes_importer.apply(log_path)
        # calculates the Matrix Container object
        mco = sna_transformer.apply(log)
        # calculates the Handover of Work matrix
        hw_matrix = handover_of_work.apply(mco)
        # calculates the Similar Activities matrix
        sim_act_matrix = similar_activities.apply(mco)


if __name__ == "__main__":
    unittest.main()

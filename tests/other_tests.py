import os
import unittest
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.log.importer.csv import factory as csv_importer
from pm4py.algo.discovery.log_skeleton import factory as lsk_factory
from pm4py.algo.conformance.log_skeleton import factory as lsk_conf_factory
from pm4py.statistics.performance_spectrum.versions import log as log_pspectrum
from pm4py.statistics.performance_spectrum.versions import dataframe as df_pspectrum


class OtherPartsTests(unittest.TestCase):
    def test_log_skeleton(self):
        log = xes_importer.apply(os.path.join("input_data", "receipt.xes"))
        skeleton = lsk_factory.apply(log)
        conf_res = lsk_conf_factory.apply(log, skeleton)


    def test_performance_spectrum_log(self):
        log = xes_importer.apply(os.path.join("input_data", "receipt.xes"))
        pspectr = log_pspectrum.apply(log, ["T02 Check confirmation of receipt", "T03 Adjust confirmation of receipt"], 1000, {})


    def test_performance_spectrum_df(self):
        log = csv_importer.import_dataframe_from_path(os.path.join("input_data", "receipt.csv"))
        pspectr = df_pspectrum.apply(log, ["T02 Check confirmation of receipt", "T03 Adjust confirmation of receipt"], 1000, {})


if __name__ == "__main__":
    unittest.main()

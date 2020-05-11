import os
import unittest
from pm4py.objects.log.importer.xes import importer as xes_importer
import pandas as pd
from pm4py.objects.log.util import dataframe_utils
from pm4py.algo.discovery.log_skeleton import algorithm as lsk_alg
from pm4py.algo.conformance.log_skeleton import algorithm as lsk_conf_alg
from pm4py.statistics.performance_spectrum.versions import log as log_pspectrum
from pm4py.statistics.performance_spectrum.versions import dataframe as df_pspectrum


class OtherPartsTests(unittest.TestCase):
    def test_log_skeleton(self):
        log = xes_importer.apply(os.path.join("input_data", "receipt.xes"))
        skeleton = lsk_alg.apply(log)
        conf_res = lsk_conf_alg.apply(log, skeleton)

    def test_performance_spectrum_log(self):
        log = xes_importer.apply(os.path.join("input_data", "receipt.xes"))
        pspectr = log_pspectrum.apply(log, ["T02 Check confirmation of receipt", "T03 Adjust confirmation of receipt"],
                                      1000, {})

    def test_performance_spectrum_df(self):
        df = pd.read_csv(os.path.join("input_data", "receipt.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df)
        pspectr = df_pspectrum.apply(df, ["T02 Check confirmation of receipt", "T03 Adjust confirmation of receipt"],
                                     1000, {})

    def test_alignment(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.alpha import algorithm as alpha_miner
        net, im, fm = alpha_miner.apply(log)
        from pm4py.algo.conformance.alignments import algorithm as alignments
        aligned_traces = alignments.apply(log, net, im, fm, variant=alignments.Variants.VERSION_STATE_EQUATION_A_STAR)
        aligned_traces = alignments.apply(log, net, im, fm, variant=alignments.Variants.VERSION_DIJKSTRA_NO_HEURISTICS)


if __name__ == "__main__":
    unittest.main()

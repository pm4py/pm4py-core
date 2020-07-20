import os
import unittest
from pm4py.objects.log.importer.xes import importer as xes_importer
import pandas as pd
from pm4py.objects.log.util import dataframe_utils
from pm4py.algo.discovery.log_skeleton import algorithm as lsk_alg
from pm4py.algo.conformance.log_skeleton import algorithm as lsk_conf_alg
from pm4py.objects.process_tree.importer import importer as ptree_importer
from pm4py.objects.process_tree.exporter import exporter as ptree_exporter
from pm4py.statistics.performance_spectrum.versions import log as log_pspectrum
from pm4py.statistics.performance_spectrum.versions import dataframe as df_pspectrum
from pm4py.objects.dfg.importer import importer as dfg_importer
from pm4py.objects.dfg.exporter import exporter as dfg_exporter
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.statistics.start_activities.log import get as start_activities
from pm4py.statistics.end_activities.log import get as end_activities
from pm4py.evaluation.earth_mover_distance import evaluator as earth_mover_distance
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.statistics.variants.log import get as variants_get
from pm4py.simulation.playout import simulator


class OtherPartsTests(unittest.TestCase):
    def test_emd_1(self):
        M = {("a", "b", "d", "e"): 0.49, ("a", "d", "b", "e"): 0.49, ("a", "c", "d", "e"): 0.01,
             ("a", "d", "c", "e"): 0.01}
        L1 = {("a", "b", "d", "e"): 0.49, ("a", "d", "b", "e"): 0.49, ("a", "c", "d", "e"): 0.01,
              ("a", "d", "c", "e"): 0.01}
        earth_mover_distance.apply(M, L1)

    def test_emd_2(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        lang_log = variants_get.get_language(log)
        net1, im1, fm1 = inductive_miner.apply(log)
        lang_model1 = variants_get.get_language(
            simulator.apply(net1, im1, fm1, variant=simulator.Variants.STOCHASTIC_PLAYOUT,
                            parameters={simulator.Variants.STOCHASTIC_PLAYOUT.value.Parameters.LOG: log}))
        emd = earth_mover_distance.apply(lang_model1, lang_log)

    def test_importing_dfg(self):
        dfg, sa, ea = dfg_importer.apply(os.path.join("input_data", "running-example.dfg"))

    def test_exporting_dfg(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        dfg = dfg_discovery.apply(log)
        dfg_exporter.apply(dfg, os.path.join("test_output_data", "running-example.dfg"))
        dfg, sa, ea = dfg_importer.apply(os.path.join("test_output_data", "running-example.dfg"))
        os.remove(os.path.join("test_output_data", "running-example.dfg"))

    def test_exporting_dfg_with_sa_ea(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        dfg = dfg_discovery.apply(log)
        sa = start_activities.get_start_activities(log)
        ea = end_activities.get_end_activities(log)
        dfg_exporter.apply(dfg, os.path.join("test_output_data", "running-example.dfg"),
                           parameters={dfg_exporter.Variants.CLASSIC.value.Parameters.START_ACTIVITIES: sa,
                                       dfg_exporter.Variants.CLASSIC.value.Parameters.END_ACTIVITIES: ea})
        dfg, sa, ea = dfg_importer.apply(os.path.join("test_output_data", "running-example.dfg"))
        os.remove(os.path.join("test_output_data", "running-example.dfg"))

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

    def test_import_export_ptml(self):
        tree = ptree_importer.apply(os.path.join("input_data", "running-example.ptml"))
        ptree_exporter.apply(tree, os.path.join("test_output_data", "running-example2.ptml"))
        os.remove(os.path.join("test_output_data", "running-example2.ptml"))


    def test_footprints_net(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.alpha import algorithm as alpha_miner
        net, im, fm = alpha_miner.apply(log)
        from pm4py.algo.discovery.footprints import algorithm as footprints_discovery
        fp_log = footprints_discovery.apply(log)
        fp_net = footprints_discovery.apply(net, im)
        from pm4py.algo.conformance.footprints import algorithm as footprints_conformance
        conf = footprints_conformance.apply(fp_log, fp_net)


if __name__ == "__main__":
    unittest.main()

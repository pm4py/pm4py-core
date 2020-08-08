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
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.statistics.variants.log import get as variants_get
from pm4py.simulation.playout import simulator
from pm4py.objects.log.adapters.pandas import csv_import_adapter
from pm4py.objects.conversion.log import converter


class OtherPartsTests(unittest.TestCase):
    def test_emd_1(self):
        from pm4py.evaluation.earth_mover_distance import evaluator as earth_mover_distance
        M = {("a", "b", "d", "e"): 0.49, ("a", "d", "b", "e"): 0.49, ("a", "c", "d", "e"): 0.01,
             ("a", "d", "c", "e"): 0.01}
        L1 = {("a", "b", "d", "e"): 0.49, ("a", "d", "b", "e"): 0.49, ("a", "c", "d", "e"): 0.01,
              ("a", "d", "c", "e"): 0.01}
        earth_mover_distance.apply(M, L1)

    def test_emd_2(self):
        from pm4py.evaluation.earth_mover_distance import evaluator as earth_mover_distance
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
        fp_entire_log = footprints_discovery.apply(log, variant=footprints_discovery.Variants.ENTIRE_EVENT_LOG)
        fp_trace_trace = footprints_discovery.apply(log)
        fp_net = footprints_discovery.apply(net, im)
        from pm4py.algo.conformance.footprints import algorithm as footprints_conformance
        conf1 = footprints_conformance.apply(fp_entire_log, fp_net)
        conf2 = footprints_conformance.apply(fp_trace_trace, fp_net)
        conf3 = footprints_conformance.apply(fp_entire_log, fp_net,
                                             variant=footprints_conformance.Variants.LOG_EXTENSIVE)
        conf4 = footprints_conformance.apply(fp_trace_trace, fp_net,
                                             variant=footprints_conformance.Variants.TRACE_EXTENSIVE)

    def test_footprints_tree(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.inductive import algorithm as inductive_miner
        tree = inductive_miner.apply_tree(log)
        from pm4py.algo.discovery.footprints import algorithm as footprints_discovery
        fp_entire_log = footprints_discovery.apply(log, variant=footprints_discovery.Variants.ENTIRE_EVENT_LOG)
        fp_trace_trace = footprints_discovery.apply(log)
        fp_tree = footprints_discovery.apply(tree)
        from pm4py.algo.conformance.footprints import algorithm as footprints_conformance
        conf1 = footprints_conformance.apply(fp_entire_log, fp_tree)
        conf2 = footprints_conformance.apply(fp_trace_trace, fp_tree)
        conf3 = footprints_conformance.apply(fp_entire_log, fp_tree,
                                             variant=footprints_conformance.Variants.LOG_EXTENSIVE)
        conf4 = footprints_conformance.apply(fp_trace_trace, fp_tree,
                                             variant=footprints_conformance.Variants.TRACE_EXTENSIVE)

    def test_footprints_tree_df(self):
        df = csv_import_adapter.import_dataframe_from_path(os.path.join("input_data", "running-example.csv"))
        from pm4py.algo.discovery.inductive import algorithm as inductive_miner
        log = converter.apply(df)
        tree = inductive_miner.apply_tree(log)
        from pm4py.algo.discovery.footprints import algorithm as footprints_discovery
        fp_df = footprints_discovery.apply(df)
        fp_tree = footprints_discovery.apply(tree)
        from pm4py.algo.conformance.footprints import algorithm as footprints_conformance
        conf = footprints_conformance.apply(fp_df, fp_tree)

    def test_playout_tree_basic(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.inductive import algorithm as inductive_miner
        tree = inductive_miner.apply_tree(log)
        from pm4py.simulation.tree_playout import algorithm as tree_playout
        new_log = tree_playout.apply(tree)

    def test_playout_tree_extensive(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.inductive import algorithm as inductive_miner
        tree = inductive_miner.apply_tree(log)
        from pm4py.simulation.tree_playout import algorithm as tree_playout
        new_log = tree_playout.apply(tree, variant=tree_playout.Variants.EXTENSIVE)


if __name__ == "__main__":
    unittest.main()

import unittest
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.conversion.process_tree import converter as process_tree_converter
from pm4py.util import constants
import os
import pandas as pd


class AlgorithmTest(unittest.TestCase):
    def test_importing_xes(self):
        from pm4py.objects.log.importer.xes import importer as xes_importer
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"),
                                 variant=xes_importer.Variants.ITERPARSE)
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"),
                                 variant=xes_importer.Variants.LINE_BY_LINE)
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"),
                                 variant=xes_importer.Variants.ITERPARSE_MEM_COMPRESSED)
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"),
                                 variant=xes_importer.Variants.CHUNK_REGEX)

    """def test_hiearch_clustering(self):
        from pm4py.algo.clustering.trace_attribute_driven import algorithm as clust_algorithm
        log = xes_importer.apply(os.path.join("input_data", "receipt.xes"), variant=xes_importer.Variants.LINE_BY_LINE,
                                 parameters={xes_importer.Variants.LINE_BY_LINE.value.Parameters.MAX_TRACES: 50})
        # raise Exception("%d" % (len(log)))
        clust_algorithm.apply(log, "responsible", variant=clust_algorithm.Variants.VARIANT_DMM_VEC)"""

    def test_log_skeleton(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.log_skeleton import algorithm as lsk_discovery
        model = lsk_discovery.apply(log)
        from pm4py.algo.conformance.log_skeleton import algorithm as lsk_conformance
        conf = lsk_conformance.apply(log, model)

    def test_alignment(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.alpha import algorithm as alpha_miner
        net, im, fm = alpha_miner.apply(log)
        from pm4py.algo.conformance.alignments.petri_net import algorithm as alignments
        aligned_traces = alignments.apply(log, net, im, fm, variant=alignments.Variants.VERSION_STATE_EQUATION_A_STAR)
        aligned_traces = alignments.apply(log, net, im, fm, variant=alignments.Variants.VERSION_DIJKSTRA_NO_HEURISTICS)
        from pm4py.algo.evaluation.replay_fitness import algorithm as rp_fitness_evaluator
        fitness = rp_fitness_evaluator.apply(log, net, im, fm, variant=rp_fitness_evaluator.Variants.ALIGNMENT_BASED)
        evaluation = rp_fitness_evaluator.evaluate(aligned_traces,
                                                   variant=rp_fitness_evaluator.Variants.ALIGNMENT_BASED)
        from pm4py.algo.evaluation.precision import algorithm as precision_evaluator
        precision = precision_evaluator.apply(log, net, im, fm, variant=rp_fitness_evaluator.Variants.ALIGNMENT_BASED)

    def test_decomp_alignment(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.alpha import algorithm as alpha_miner
        net, im, fm = alpha_miner.apply(log)
        from pm4py.algo.conformance.alignments.decomposed import algorithm as decomp_align
        aligned_traces = decomp_align.apply(log, net, im, fm, variant=decomp_align.Variants.RECOMPOS_MAXIMAL)

    def test_tokenreplay(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.alpha import algorithm as alpha_miner
        net, im, fm = alpha_miner.apply(log)
        from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
        replayed_traces = token_replay.apply(log, net, im, fm, variant=token_replay.Variants.TOKEN_REPLAY)
        replayed_traces = token_replay.apply(log, net, im, fm, variant=token_replay.Variants.BACKWARDS)
        from pm4py.algo.evaluation.replay_fitness import algorithm as rp_fitness_evaluator
        fitness = rp_fitness_evaluator.apply(log, net, im, fm, variant=rp_fitness_evaluator.Variants.TOKEN_BASED)
        evaluation = rp_fitness_evaluator.evaluate(replayed_traces, variant=rp_fitness_evaluator.Variants.TOKEN_BASED)
        from pm4py.algo.evaluation.precision import algorithm as precision_evaluator
        precision = precision_evaluator.apply(log, net, im, fm,
                                              variant=precision_evaluator.Variants.ETCONFORMANCE_TOKEN)
        from pm4py.algo.evaluation.generalization import algorithm as generalization_evaluation
        generalization = generalization_evaluation.apply(log, net, im, fm,
                                                         variant=generalization_evaluation.Variants.GENERALIZATION_TOKEN)

    def test_evaluation(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.alpha import algorithm as alpha_miner
        net, im, fm = alpha_miner.apply(log)
        from pm4py.algo.evaluation.simplicity import algorithm as simplicity
        simp = simplicity.apply(net)
        from pm4py.algo.evaluation import algorithm as evaluation_method
        eval = evaluation_method.apply(log, net, im, fm)

    def test_playout(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.alpha import algorithm as alpha_miner
        net, im, fm = alpha_miner.apply(log)
        from pm4py.algo.simulation.playout.petri_net import algorithm
        log2 = algorithm.apply(net, im, fm)

    def test_tree_generation(self):
        from pm4py.algo.simulation.tree_generator import algorithm as tree_simulator
        tree1 = tree_simulator.apply(variant=tree_simulator.Variants.BASIC)
        tree2 = tree_simulator.apply(variant=tree_simulator.Variants.PTANDLOGGENERATOR)

    def test_alpha_miner_log(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.alpha import algorithm as alpha_miner
        net1, im1, fm1 = alpha_miner.apply(log, variant=alpha_miner.Variants.ALPHA_VERSION_CLASSIC)
        net2, im2, fm2 = alpha_miner.apply(log, variant=alpha_miner.Variants.ALPHA_VERSION_PLUS)
        from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
        dfg = dfg_discovery.apply(log)
        net3, im3, fm3 = alpha_miner.apply_dfg(dfg, variant=alpha_miner.Variants.ALPHA_VERSION_CLASSIC)

    def test_alpha_miner_dataframe(self):
        df = pd.read_csv(os.path.join("input_data", "running-example.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format="ISO8601")
        from pm4py.algo.discovery.alpha import algorithm as alpha_miner
        net, im, fm = alpha_miner.apply(df, variant=alpha_miner.Variants.ALPHA_VERSION_CLASSIC)

    def test_tsystem(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.transition_system import algorithm as ts_system
        tsystem = ts_system.apply(log, variant=ts_system.Variants.VIEW_BASED)

    def test_inductive_miner(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.inductive import algorithm as inductive_miner
        process_tree = inductive_miner.apply(log)
        net, im, fm = process_tree_converter.apply(process_tree)

    def test_performance_spectrum(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.performance_spectrum import algorithm as pspectrum
        ps = pspectrum.apply(log, ["register request", "decide"])
        df = pd.read_csv(os.path.join("input_data", "running-example.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format="ISO8601")
        ps = pspectrum.apply(df, ["register request", "decide"])

if __name__ == "__main__":
    unittest.main()

import os
import unittest

from pm4py.algo.conformance.alignments.petri_net import algorithm as align_alg
from pm4py.algo.conformance.tokenreplay import algorithm as tr_alg
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.algo.discovery.dfg import algorithm as dfg_mining
from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.discovery.transition_system import algorithm as ts_disc
from pm4py.algo.evaluation import algorithm as eval_alg
from pm4py.algo.evaluation.generalization import algorithm as generalization
from pm4py.algo.evaluation.precision import algorithm as precision_evaluator
from pm4py.algo.evaluation.replay_fitness import algorithm as rp_fit
from pm4py.algo.evaluation.simplicity import algorithm as simplicity
from pm4py.objects.conversion.log import converter as log_conversion
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.util import dataframe_utils
from pm4py.util import constants, pandas_utils
from pm4py.objects.conversion.process_tree import converter as process_tree_converter


class MainFactoriesTest(unittest.TestCase):
    def test_nonstandard_exporter(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        xes_exporter.apply(log, os.path.join("test_output_data", "running-example.xes"),
                           variant=xes_exporter.Variants.LINE_BY_LINE)
        os.remove(os.path.join("test_output_data", "running-example.xes"))

    def test_alphaminer_log(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        net, im, fm = alpha_miner.apply(log)
        aligned_traces_tr = tr_alg.apply(log, net, im, fm)
        aligned_traces_alignments = align_alg.apply(log, net, im, fm)
        evaluation = eval_alg.apply(log, net, im, fm)
        fitness = rp_fit.apply(log, net, im, fm)
        precision = precision_evaluator.apply(log, net, im, fm)
        gen = generalization.apply(log, net, im, fm)
        sim = simplicity.apply(net)

    def test_memory_efficient_iterparse(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"),
                                 variant=xes_importer.Variants.ITERPARSE_MEM_COMPRESSED)

    def test_alphaminer_stream(self):
        df = pandas_utils.read_csv(os.path.join("input_data", "running-example.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        stream = log_conversion.apply(df, variant=log_conversion.TO_EVENT_STREAM)
        net, im, fm = alpha_miner.apply(stream)
        aligned_traces_tr = tr_alg.apply(stream, net, im, fm)
        aligned_traces_alignments = align_alg.apply(stream, net, im, fm)
        evaluation = eval_alg.apply(stream, net, im, fm)
        fitness = rp_fit.apply(stream, net, im, fm)
        precision = precision_evaluator.apply(stream, net, im, fm)
        gen = generalization.apply(stream, net, im, fm)
        sim = simplicity.apply(net)

    def test_alphaminer_df(self):
        log = pandas_utils.read_csv(os.path.join("input_data", "running-example.csv"))
        log = dataframe_utils.convert_timestamp_columns_in_df(log, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        net, im, fm = alpha_miner.apply(log)
        aligned_traces_tr = tr_alg.apply(log, net, im, fm)
        aligned_traces_alignments = align_alg.apply(log, net, im, fm)
        evaluation = eval_alg.apply(log, net, im, fm)
        fitness = rp_fit.apply(log, net, im, fm)
        precision = precision_evaluator.apply(log, net, im, fm)
        gen = generalization.apply(log, net, im, fm)
        sim = simplicity.apply(net)

    def test_inductiveminer_log(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        process_tree = inductive_miner.apply(log)
        net, im, fm = process_tree_converter.apply(process_tree)
        aligned_traces_tr = tr_alg.apply(log, net, im, fm)
        aligned_traces_alignments = align_alg.apply(log, net, im, fm)
        evaluation = eval_alg.apply(log, net, im, fm)
        fitness = rp_fit.apply(log, net, im, fm)
        precision = precision_evaluator.apply(log, net, im, fm)
        gen = generalization.apply(log, net, im, fm)
        sim = simplicity.apply(net)

    def test_inductiveminer_df(self):
        log = pandas_utils.read_csv(os.path.join("input_data", "running-example.csv"))
        log = dataframe_utils.convert_timestamp_columns_in_df(log, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        process_tree = inductive_miner.apply(log)
        net, im, fm = process_tree_converter.apply(process_tree)
        aligned_traces_tr = tr_alg.apply(log, net, im, fm)
        aligned_traces_alignments = align_alg.apply(log, net, im, fm)
        evaluation = eval_alg.apply(log, net, im, fm)
        fitness = rp_fit.apply(log, net, im, fm)
        precision = precision_evaluator.apply(log, net, im, fm)
        gen = generalization.apply(log, net, im, fm)
        sim = simplicity.apply(net)

    def test_heu_log(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        net, im, fm = heuristics_miner.apply(log)
        aligned_traces_tr = tr_alg.apply(log, net, im, fm)
        aligned_traces_alignments = align_alg.apply(log, net, im, fm)
        evaluation = eval_alg.apply(log, net, im, fm)
        fitness = rp_fit.apply(log, net, im, fm)
        precision = precision_evaluator.apply(log, net, im, fm)
        gen = generalization.apply(log, net, im, fm)
        sim = simplicity.apply(net)

    def test_heu_stream(self):
        df = pandas_utils.read_csv(os.path.join("input_data", "running-example.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        stream = log_conversion.apply(df, variant=log_conversion.TO_EVENT_STREAM)
        net, im, fm = heuristics_miner.apply(stream)
        aligned_traces_tr = tr_alg.apply(stream, net, im, fm)
        aligned_traces_alignments = align_alg.apply(stream, net, im, fm)
        evaluation = eval_alg.apply(stream, net, im, fm)
        fitness = rp_fit.apply(stream, net, im, fm)
        precision = precision_evaluator.apply(stream, net, im, fm)
        gen = generalization.apply(stream, net, im, fm)
        sim = simplicity.apply(net)

    def test_heu_df(self):
        log = pandas_utils.read_csv(os.path.join("input_data", "running-example.csv"))
        log = dataframe_utils.convert_timestamp_columns_in_df(log, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        net, im, fm = heuristics_miner.apply(log)
        aligned_traces_tr = tr_alg.apply(log, net, im, fm)
        aligned_traces_alignments = align_alg.apply(log, net, im, fm)
        evaluation = eval_alg.apply(log, net, im, fm)
        fitness = rp_fit.apply(log, net, im, fm)
        precision = precision_evaluator.apply(log, net, im, fm)
        gen = generalization.apply(log, net, im, fm)
        sim = simplicity.apply(net)

    def test_dfg_log(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        dfg = dfg_mining.apply(log)

    def test_dfg_stream(self):
        df = pandas_utils.read_csv(os.path.join("input_data", "running-example.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        stream = log_conversion.apply(df, variant=log_conversion.TO_EVENT_STREAM)
        dfg = dfg_mining.apply(stream)

    def test_dfg_df(self):
        df = pandas_utils.read_csv(os.path.join("input_data", "running-example.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        dfg = dfg_mining.apply(df)

    def test_ts_log(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        ts = ts_disc.apply(log)

    def test_ts_stream(self):
        df = pandas_utils.read_csv(os.path.join("input_data", "running-example.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        stream = log_conversion.apply(df, variant=log_conversion.TO_EVENT_STREAM)
        ts = ts_disc.apply(stream)

    def test_ts_df(self):
        df = pandas_utils.read_csv(os.path.join("input_data", "running-example.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        ts = ts_disc.apply(df)

    def test_csvimp_xesexp(self):
        df = pandas_utils.read_csv(os.path.join("input_data", "running-example.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        log0 = log_conversion.apply(df, variant=log_conversion.TO_EVENT_STREAM)
        log = log_conversion.apply(log0, variant=log_conversion.TO_EVENT_LOG)
        stream = log_conversion.apply(log0, variant=log_conversion.TO_EVENT_STREAM)
        df = log_conversion.apply(log0, variant=log_conversion.TO_DATA_FRAME)
        xes_exporter.apply(log, "ru.xes")
        xes_exporter.apply(stream, "ru.xes")
        xes_exporter.apply(df, "ru.xes")
        os.remove('ru.xes')

    def test_xesimp_xesexp(self):
        log0 = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        log = log_conversion.apply(log0, variant=log_conversion.TO_EVENT_LOG)
        stream = log_conversion.apply(log0, variant=log_conversion.TO_EVENT_STREAM)
        df = log_conversion.apply(log0, variant=log_conversion.TO_DATA_FRAME)
        xes_exporter.apply(log, "ru.xes")
        xes_exporter.apply(stream, "ru.xes")
        xes_exporter.apply(df, "ru.xes")
        os.remove('ru.xes')

    def test_pdimp_xesexp(self):
        log0 = pandas_utils.read_csv(os.path.join("input_data", "running-example.csv"))
        log0 = dataframe_utils.convert_timestamp_columns_in_df(log0, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        log = log_conversion.apply(log0, variant=log_conversion.TO_EVENT_LOG)
        stream = log_conversion.apply(log0, variant=log_conversion.TO_EVENT_STREAM)
        df = log_conversion.apply(log0, variant=log_conversion.TO_DATA_FRAME)
        xes_exporter.apply(log, "ru.xes")
        xes_exporter.apply(stream, "ru.xes")
        xes_exporter.apply(df, "ru.xes")
        os.remove('ru.xes')


if __name__ == "__main__":
    unittest.main()

import os
import unittest
from pm4py.objects.log.importer.xes import algorithm as xes_importer
from pm4py.objects.log.importer.csv import algorithm as csv_importer
from pm4py.objects.log.adapters.pandas import csv_import_adapter
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
from pm4py.algo.discovery.dfg import algorithm as dfg_mining
from pm4py.algo.discovery.transition_system import algorithm as ts_disc
from pm4py.algo.conformance.alignments import algorithm as align_alg
from pm4py.algo.conformance.tokenreplay import algorithm as tr_alg
from pm4py.evaluation import algorithm as eval_alg
from pm4py.evaluation.replay_fitness import algorithm as rp_fit
from pm4py.evaluation.precision import algorithm as precision_factory
from pm4py.evaluation.generalization import algorithm as generalization
from pm4py.evaluation.simplicity import algorithm as simplicity
from pm4py.objects.conversion.log import algorithm as log_conversion
from pm4py.objects.log.exporter.csv import algorithm as csv_exporter
from pm4py.objects.log.exporter.xes import algorithm as xes_exporter


class MainFactoriesTest(unittest.TestCase):
    def test_alphaminer_log(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        net, im, fm = alpha_miner.apply(log)
        aligned_traces_tr = tr_alg.apply(log, net, im, fm)
        aligned_traces_alignments = align_alg.apply(log, net, im, fm)
        evaluation = eval_alg.apply(log, net, im, fm)
        fitness = rp_fit.apply(log, net, im, fm)
        precision = precision_factory.apply(log, net, im, fm)
        generalization = generalization.apply(log, net, im, fm)
        simplicity = simplicity.apply(net)

    def test_alphaminer_stream(self):
        stream = csv_importer.apply(os.path.join("input_data", "running-example.csv"))
        net, im, fm = alpha_miner.apply(stream)
        aligned_traces_tr = tr_alg.apply(stream, net, im, fm)
        aligned_traces_alignments = align_alg.apply(stream, net, im, fm)
        evaluation = eval_alg.apply(stream, net, im, fm)
        fitness = rp_fit.apply(stream, net, im, fm)
        precision = precision_factory.apply(stream, net, im, fm)
        generalization = generalization.apply(stream, net, im, fm)
        simplicity = simplicity.apply(net)

    def test_alphaminer_df(self):
        log = csv_import_adapter.import_dataframe_from_path(os.path.join("input_data", "running-example.csv"))
        net, im, fm = alpha_miner.apply(log)
        aligned_traces_tr = tr_alg.apply(log, net, im, fm)
        aligned_traces_alignments = align_alg.apply(log, net, im, fm)
        evaluation = eval_alg.apply(log, net, im, fm)
        fitness = rp_fit.apply(log, net, im, fm)
        precision = precision_factory.apply(log, net, im, fm)
        generalization = generalization.apply(log, net, im, fm)
        simplicity = simplicity.apply(net)

    def test_inductiveminer_log(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        net, im, fm = inductive_miner.apply(log)
        aligned_traces_tr = tr_alg.apply(log, net, im, fm)
        aligned_traces_alignments = align_alg.apply(log, net, im, fm)
        evaluation = eval_alg.apply(log, net, im, fm)
        fitness = rp_fit.apply(log, net, im, fm)
        precision = precision_factory.apply(log, net, im, fm)
        generalization = generalization.apply(log, net, im, fm)
        simplicity = simplicity.apply(net)

    def test_inductiveminer_stream(self):
        stream = csv_importer.apply(os.path.join("input_data", "running-example.csv"))
        net, im, fm = inductive_miner.apply(stream)
        aligned_traces_tr = tr_alg.apply(stream, net, im, fm)
        aligned_traces_alignments = align_alg.apply(stream, net, im, fm)
        evaluation = eval_alg.apply(stream, net, im, fm)
        fitness = rp_fit.apply(stream, net, im, fm)
        precision = precision_factory.apply(stream, net, im, fm)
        generalization = generalization.apply(stream, net, im, fm)
        simplicity = simplicity.apply(net)

    def test_inductiveminer_df(self):
        log = csv_import_adapter.import_dataframe_from_path(os.path.join("input_data", "running-example.csv"))
        net, im, fm = inductive_miner.apply(log)
        aligned_traces_tr = tr_alg.apply(log, net, im, fm)
        aligned_traces_alignments = align_alg.apply(log, net, im, fm)
        evaluation = eval_alg.apply(log, net, im, fm)
        fitness = rp_fit.apply(log, net, im, fm)
        precision = precision_factory.apply(log, net, im, fm)
        generalization = generalization.apply(log, net, im, fm)
        simplicity = simplicity.apply(net)

    def test_heu_log(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        net, im, fm = heuristics_miner.apply(log)
        aligned_traces_tr = tr_alg.apply(log, net, im, fm)
        aligned_traces_alignments = align_alg.apply(log, net, im, fm)
        evaluation = eval_alg.apply(log, net, im, fm)
        fitness = rp_fit.apply(log, net, im, fm)
        precision = precision_factory.apply(log, net, im, fm)
        generalization = generalization.apply(log, net, im, fm)
        simplicity = simplicity.apply(net)

    def test_heu_stream(self):
        stream = csv_importer.apply(os.path.join("input_data", "running-example.csv"))
        net, im, fm = heuristics_miner.apply(stream)
        aligned_traces_tr = tr_alg.apply(stream, net, im, fm)
        aligned_traces_alignments = align_alg.apply(stream, net, im, fm)
        evaluation = eval_alg.apply(stream, net, im, fm)
        fitness = rp_fit.apply(stream, net, im, fm)
        precision = precision_factory.apply(stream, net, im, fm)
        generalization = generalization.apply(stream, net, im, fm)
        simplicity = simplicity.apply(net)

    def test_heu_df(self):
        log = csv_import_adapter.import_dataframe_from_path(os.path.join("input_data", "running-example.csv"))
        net, im, fm = heuristics_miner.apply(log)
        aligned_traces_tr = tr_alg.apply(log, net, im, fm)
        aligned_traces_alignments = align_alg.apply(log, net, im, fm)
        evaluation = eval_alg.apply(log, net, im, fm)
        fitness = rp_fit.apply(log, net, im, fm)
        precision = precision_factory.apply(log, net, im, fm)
        generalization = generalization.apply(log, net, im, fm)
        simplicity = simplicity.apply(net)

    def test_dfg_log(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        dfg = dfg_mining.apply(log)

    def test_dfg_stream(self):
        stream = csv_importer.apply(os.path.join("input_data", "running-example.csv"))
        dfg = dfg_mining.apply(stream)

    def test_dfg_df(self):
        log = csv_import_adapter.import_dataframe_from_path(os.path.join("input_data", "running-example.csv"))
        dfg = dfg_mining.apply(log)

    def test_ts_log(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        ts = ts_disc.apply(log)

    def test_ts_stream(self):
        stream = csv_importer.apply(os.path.join("input_data", "running-example.csv"))
        ts = ts_disc.apply(stream)

    def test_ts_df(self):
        log = csv_import_adapter.import_dataframe_from_path(os.path.join("input_data", "running-example.csv"))
        ts = ts_disc.apply(log)

    def test_csvimp_csvexp(self):
        log0 = csv_importer.apply(os.path.join("input_data", "running-example.csv"))
        log = log_conversion.apply(log0, variant=log_conversion.TO_EVENT_LOG)
        stream = log_conversion.apply(log0, variant=log_conversion.TO_EVENT_STREAM)
        df = log_conversion.apply(log0, variant=log_conversion.TO_DATAFRAME)
        csv_exporter.export(log, "ru.csv")
        csv_exporter.export(stream, "ru.csv")
        csv_exporter.export(df, "ru.csv")
        os.remove('ru.csv')

    def test_csvimp_xesexp(self):
        log0 = csv_importer.apply(os.path.join("input_data", "running-example.csv"))
        log = log_conversion.apply(log0, variant=log_conversion.TO_EVENT_LOG)
        stream = log_conversion.apply(log0, variant=log_conversion.TO_EVENT_STREAM)
        df = log_conversion.apply(log0, variant=log_conversion.TO_DATAFRAME)
        xes_exporter.apply(log, "ru.xes")
        xes_exporter.apply(stream, "ru.xes")
        xes_exporter.apply(df, "ru.xes")
        os.remove('ru.xes')

    def test_xesimp_csvexp(self):
        log0 = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        log = log_conversion.apply(log0, variant=log_conversion.TO_EVENT_LOG)
        stream = log_conversion.apply(log0, variant=log_conversion.TO_EVENT_STREAM)
        df = log_conversion.apply(log0, variant=log_conversion.TO_DATAFRAME)
        csv_exporter.export(log, "ru.csv")
        csv_exporter.export(stream, "ru.csv")
        csv_exporter.export(df, "ru.csv")
        os.remove('ru.csv')

    def test_xesimp_xesexp(self):
        log0 = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        log = log_conversion.apply(log0, variant=log_conversion.TO_EVENT_LOG)
        stream = log_conversion.apply(log0, variant=log_conversion.TO_EVENT_STREAM)
        df = log_conversion.apply(log0, variant=log_conversion.TO_DATAFRAME)
        xes_exporter.apply(log, "ru.xes")
        xes_exporter.apply(stream, "ru.xes")
        xes_exporter.apply(df, "ru.xes")
        os.remove('ru.xes')

    def test_pdimp_csvexp(self):
        log0 = csv_import_adapter.import_dataframe_from_path(os.path.join("input_data", "running-example.csv"))
        log = log_conversion.apply(log0, variant=log_conversion.TO_EVENT_LOG)
        stream = log_conversion.apply(log0, variant=log_conversion.TO_EVENT_STREAM)
        df = log_conversion.apply(log0, variant=log_conversion.TO_DATAFRAME)
        csv_exporter.export(log, "ru.csv")
        csv_exporter.export(stream, "ru.csv")
        csv_exporter.export(df, "ru.csv")
        os.remove('ru.csv')

    def test_pdimp_xesexp(self):
        log0 = csv_import_adapter.import_dataframe_from_path(os.path.join("input_data", "running-example.csv"))
        log = log_conversion.apply(log0, variant=log_conversion.TO_EVENT_LOG)
        stream = log_conversion.apply(log0, variant=log_conversion.TO_EVENT_STREAM)
        df = log_conversion.apply(log0, variant=log_conversion.TO_DATAFRAME)
        xes_exporter.apply(log, "ru.xes")
        xes_exporter.apply(stream, "ru.xes")
        xes_exporter.apply(df, "ru.xes")
        os.remove('ru.xes')


if __name__ == "__main__":
    unittest.main()

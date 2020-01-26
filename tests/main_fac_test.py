import os
import unittest
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.log.importer.csv import factory as csv_importer
from pm4py.objects.log.adapters.pandas import csv_import_adapter
from pm4py.algo.discovery.alpha import factory as alpha_miner
from pm4py.algo.discovery.inductive import factory as inductive_miner
from pm4py.algo.discovery.heuristics import factory as heuristics_miner
from pm4py.algo.discovery.dfg import factory as dfg_mining_factory
from pm4py.algo.discovery.transition_system import factory as ts_disc_factory
from pm4py.algo.conformance.alignments import factory as align_factory
from pm4py.algo.conformance.tokenreplay import factory as tr_factory
from pm4py.evaluation import factory as eval_factory
from pm4py.evaluation.replay_fitness import factory as rp_fit_factory
from pm4py.evaluation.precision import factory as precision_factory
from pm4py.evaluation.generalization import factory as generalization_factory
from pm4py.evaluation.simplicity import factory as simplicity_factory
from pm4py.objects.conversion.log import factory as log_conv_factory
from pm4py.objects.log.exporter.csv import factory as csv_exporter_factory
from pm4py.objects.log.exporter.xes import factory as xes_exporter_factory


class MainFactoriesTest(unittest.TestCase):
    def test_alphaminer_log(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        net, im, fm = alpha_miner.apply(log)
        aligned_traces_tr = tr_factory.apply(log, net, im, fm)
        aligned_traces_alignments = align_factory.apply(log, net, im, fm)
        evaluation = eval_factory.apply(log, net, im, fm)
        fitness = rp_fit_factory.apply(log, net, im, fm)
        precision = precision_factory.apply(log, net, im, fm)
        generalization = generalization_factory.apply(log, net, im, fm)
        simplicity = simplicity_factory.apply(net)

    def test_alphaminer_stream(self):
        stream = csv_importer.apply(os.path.join("input_data", "running-example.csv"))
        net, im, fm = alpha_miner.apply(stream)
        aligned_traces_tr = tr_factory.apply(stream, net, im, fm)
        aligned_traces_alignments = align_factory.apply(stream, net, im, fm)
        evaluation = eval_factory.apply(stream, net, im, fm)
        fitness = rp_fit_factory.apply(stream, net, im, fm)
        precision = precision_factory.apply(stream, net, im, fm)
        generalization = generalization_factory.apply(stream, net, im, fm)
        simplicity = simplicity_factory.apply(net)

    def test_alphaminer_df(self):
        log = csv_import_adapter.import_dataframe_from_path(os.path.join("input_data", "running-example.csv"))
        net, im, fm = alpha_miner.apply(log)
        aligned_traces_tr = tr_factory.apply(log, net, im, fm)
        aligned_traces_alignments = align_factory.apply(log, net, im, fm)
        evaluation = eval_factory.apply(log, net, im, fm)
        fitness = rp_fit_factory.apply(log, net, im, fm)
        precision = precision_factory.apply(log, net, im, fm)
        generalization = generalization_factory.apply(log, net, im, fm)
        simplicity = simplicity_factory.apply(net)

    def test_inductiveminer_log(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        net, im, fm = inductive_miner.apply(log)
        aligned_traces_tr = tr_factory.apply(log, net, im, fm)
        aligned_traces_alignments = align_factory.apply(log, net, im, fm)
        evaluation = eval_factory.apply(log, net, im, fm)
        fitness = rp_fit_factory.apply(log, net, im, fm)
        precision = precision_factory.apply(log, net, im, fm)
        generalization = generalization_factory.apply(log, net, im, fm)
        simplicity = simplicity_factory.apply(net)

    def test_inductiveminer_stream(self):
        stream = csv_importer.apply(os.path.join("input_data", "running-example.csv"))
        net, im, fm = inductive_miner.apply(stream)
        aligned_traces_tr = tr_factory.apply(stream, net, im, fm)
        aligned_traces_alignments = align_factory.apply(stream, net, im, fm)
        evaluation = eval_factory.apply(stream, net, im, fm)
        fitness = rp_fit_factory.apply(stream, net, im, fm)
        precision = precision_factory.apply(stream, net, im, fm)
        generalization = generalization_factory.apply(stream, net, im, fm)
        simplicity = simplicity_factory.apply(net)

    def test_inductiveminer_df(self):
        log = csv_import_adapter.import_dataframe_from_path(os.path.join("input_data", "running-example.csv"))
        net, im, fm = inductive_miner.apply(log)
        aligned_traces_tr = tr_factory.apply(log, net, im, fm)
        aligned_traces_alignments = align_factory.apply(log, net, im, fm)
        evaluation = eval_factory.apply(log, net, im, fm)
        fitness = rp_fit_factory.apply(log, net, im, fm)
        precision = precision_factory.apply(log, net, im, fm)
        generalization = generalization_factory.apply(log, net, im, fm)
        simplicity = simplicity_factory.apply(net)

    def test_heu_log(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        net, im, fm = heuristics_miner.apply(log)
        aligned_traces_tr = tr_factory.apply(log, net, im, fm)
        aligned_traces_alignments = align_factory.apply(log, net, im, fm)
        evaluation = eval_factory.apply(log, net, im, fm)
        fitness = rp_fit_factory.apply(log, net, im, fm)
        precision = precision_factory.apply(log, net, im, fm)
        generalization = generalization_factory.apply(log, net, im, fm)
        simplicity = simplicity_factory.apply(net)

    def test_heu_stream(self):
        stream = csv_importer.apply(os.path.join("input_data", "running-example.csv"))
        net, im, fm = heuristics_miner.apply(stream)
        aligned_traces_tr = tr_factory.apply(stream, net, im, fm)
        aligned_traces_alignments = align_factory.apply(stream, net, im, fm)
        evaluation = eval_factory.apply(stream, net, im, fm)
        fitness = rp_fit_factory.apply(stream, net, im, fm)
        precision = precision_factory.apply(stream, net, im, fm)
        generalization = generalization_factory.apply(stream, net, im, fm)
        simplicity = simplicity_factory.apply(net)

    def test_heu_df(self):
        log = csv_import_adapter.import_dataframe_from_path(os.path.join("input_data", "running-example.csv"))
        net, im, fm = heuristics_miner.apply(log)
        aligned_traces_tr = tr_factory.apply(log, net, im, fm)
        aligned_traces_alignments = align_factory.apply(log, net, im, fm)
        evaluation = eval_factory.apply(log, net, im, fm)
        fitness = rp_fit_factory.apply(log, net, im, fm)
        precision = precision_factory.apply(log, net, im, fm)
        generalization = generalization_factory.apply(log, net, im, fm)
        simplicity = simplicity_factory.apply(net)

    def test_dfg_log(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        dfg = dfg_mining_factory.apply(log)

    def test_dfg_stream(self):
        stream = csv_importer.apply(os.path.join("input_data", "running-example.csv"))
        dfg = dfg_mining_factory.apply(stream)

    def test_dfg_df(self):
        log = csv_import_adapter.import_dataframe_from_path(os.path.join("input_data", "running-example.csv"))
        dfg = dfg_mining_factory.apply(log)

    def test_ts_log(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        ts = ts_disc_factory.apply(log)

    def test_ts_stream(self):
        stream = csv_importer.apply(os.path.join("input_data", "running-example.csv"))
        ts = ts_disc_factory.apply(stream)

    def test_ts_df(self):
        log = csv_import_adapter.import_dataframe_from_path(os.path.join("input_data", "running-example.csv"))
        ts = ts_disc_factory.apply(log)

    def test_csvimp_csvexp(self):
        log0 = csv_importer.apply(os.path.join("input_data", "running-example.csv"))
        log = log_conv_factory.apply(log0, variant=log_conv_factory.TO_EVENT_LOG)
        stream = log_conv_factory.apply(log0, variant=log_conv_factory.TO_EVENT_STREAM)
        df = log_conv_factory.apply(log0, variant=log_conv_factory.TO_DATAFRAME)
        csv_exporter_factory.export(log, "ru.csv")
        csv_exporter_factory.export(stream, "ru.csv")
        csv_exporter_factory.export(df, "ru.csv")
        os.remove('ru.csv')

    def test_csvimp_xesexp(self):
        log0 = csv_importer.apply(os.path.join("input_data", "running-example.csv"))
        log = log_conv_factory.apply(log0, variant=log_conv_factory.TO_EVENT_LOG)
        stream = log_conv_factory.apply(log0, variant=log_conv_factory.TO_EVENT_STREAM)
        df = log_conv_factory.apply(log0, variant=log_conv_factory.TO_DATAFRAME)
        xes_exporter_factory.apply(log, "ru.xes")
        xes_exporter_factory.apply(stream, "ru.xes")
        xes_exporter_factory.apply(df, "ru.xes")
        os.remove('ru.xes')

    def test_xesimp_csvexp(self):
        log0 = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        log = log_conv_factory.apply(log0, variant=log_conv_factory.TO_EVENT_LOG)
        stream = log_conv_factory.apply(log0, variant=log_conv_factory.TO_EVENT_STREAM)
        df = log_conv_factory.apply(log0, variant=log_conv_factory.TO_DATAFRAME)
        csv_exporter_factory.export(log, "ru.csv")
        csv_exporter_factory.export(stream, "ru.csv")
        csv_exporter_factory.export(df, "ru.csv")
        os.remove('ru.csv')

    def test_xesimp_xesexp(self):
        log0 = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        log = log_conv_factory.apply(log0, variant=log_conv_factory.TO_EVENT_LOG)
        stream = log_conv_factory.apply(log0, variant=log_conv_factory.TO_EVENT_STREAM)
        df = log_conv_factory.apply(log0, variant=log_conv_factory.TO_DATAFRAME)
        xes_exporter_factory.apply(log, "ru.xes")
        xes_exporter_factory.apply(stream, "ru.xes")
        xes_exporter_factory.apply(df, "ru.xes")
        os.remove('ru.xes')

    def test_pdimp_csvexp(self):
        log0 = csv_import_adapter.import_dataframe_from_path(os.path.join("input_data", "running-example.csv"))
        log = log_conv_factory.apply(log0, variant=log_conv_factory.TO_EVENT_LOG)
        stream = log_conv_factory.apply(log0, variant=log_conv_factory.TO_EVENT_STREAM)
        df = log_conv_factory.apply(log0, variant=log_conv_factory.TO_DATAFRAME)
        csv_exporter_factory.export(log, "ru.csv")
        csv_exporter_factory.export(stream, "ru.csv")
        csv_exporter_factory.export(df, "ru.csv")
        os.remove('ru.csv')

    def test_pdimp_xesexp(self):
        log0 = csv_import_adapter.import_dataframe_from_path(os.path.join("input_data", "running-example.csv"))
        log = log_conv_factory.apply(log0, variant=log_conv_factory.TO_EVENT_LOG)
        stream = log_conv_factory.apply(log0, variant=log_conv_factory.TO_EVENT_STREAM)
        df = log_conv_factory.apply(log0, variant=log_conv_factory.TO_DATAFRAME)
        xes_exporter_factory.apply(log, "ru.xes")
        xes_exporter_factory.apply(stream, "ru.xes")
        xes_exporter_factory.apply(df, "ru.xes")
        os.remove('ru.xes')


if __name__ == "__main__":
    unittest.main()
